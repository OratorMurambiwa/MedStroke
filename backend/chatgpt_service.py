import os
import openai
from typing import Dict, Any, Optional
from datetime import datetime
import json
import re

class ChatGPTTreatmentPlanService:
    def __init__(self):
        # Initialize OpenAI client
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key or self.api_key == "your_openai_api_key_here":
            self.api_key = None
            print("Warning: OPENAI_API_KEY not configured. AI features will be disabled.")
        else:
            openai.api_key = self.api_key
    
    def _clean_markdown(self, text: str) -> str:
        """
        Clean markdown formatting from AI response to make it professional and readable.
        """
        if not text:
            return text
        
        # Remove markdown headers (# ## ###) - handle with or without space after
        text = re.sub(r'^#{1,6}\s*', '', text, flags=re.MULTILINE)
        
        # Remove markdown bold (**text** or __text__)
        text = re.sub(r'\*\*(.*?)\*\*', r'\1', text, flags=re.DOTALL)
        text = re.sub(r'__(.*?)__', r'\1', text, flags=re.DOTALL)
        
        # Remove markdown italic (*text* or _text_) - be careful with standalone asterisks
        # Only match if it's clearly italic (not part of **bold**)
        text = re.sub(r'(?<!\*)\*(?!\*)([^*\n]+?)(?<!\*)\*(?!\*)', r'\1', text)
        text = re.sub(r'(?<!_)_(?!_)([^_\n]+?)(?<!_)_(?!_)', r'\1', text)
        
        # Remove markdown list markers (- * +) but keep the content
        text = re.sub(r'^[\s]*[-*+]\s+', '', text, flags=re.MULTILINE)
        
        # Remove markdown numbered lists (1. 2. etc.)
        text = re.sub(r'^\d+\.\s+', '', text, flags=re.MULTILINE)
        
        # Remove markdown code blocks (```code```)
        text = re.sub(r'```[\s\S]*?```', '', text)
        
        # Remove markdown inline code (`code`)
        text = re.sub(r'`([^`]+)`', r'\1', text)
        
        # Remove markdown links [text](url) -> text
        text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
        
        # Remove any remaining standalone # characters at start of lines
        text = re.sub(r'^#+\s*', '', text, flags=re.MULTILINE)
        
        # Clean up extra whitespace
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = re.sub(r'[ \t]+', ' ', text)
        
        # Trim each line
        lines = [line.strip() for line in text.split('\n')]
        text = '\n'.join(lines)
        
        return text.strip()
    
    def generate_treatment_plan(self, patient_data: Dict[str, Any], scan_data: Dict[str, Any], 
                              eligibility_result: str, is_eligible: bool) -> str:
        """
        Generate a comprehensive treatment plan using ChatGPT based on patient data and scan results.
        """
        if not self.api_key:
            return "AI service is not configured. Please set OPENAI_API_KEY environment variable."
        
        try:
            # Prepare the prompt based on eligibility
            if is_eligible:
                prompt = self._create_tpa_eligible_prompt(patient_data, scan_data, eligibility_result)
            else:
                prompt = self._create_not_eligible_prompt(patient_data, scan_data, eligibility_result)
            
            # Call OpenAI API
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system", 
                        "content": "You are a stroke neurologist. Use the user-provided patient context only to inform your reasoning. Never repeat the context verbatim. Output must contain only the seven clinical sections requested, each with actionable treatment steps. No patient demographics, no introductions, no markdown."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                max_tokens=600,   # keeps it short
                temperature=0.1   # keeps it clinical
            )

            raw_response = response.choices[0].message.content.strip()
            
            # Clean any markdown that might still be present
            cleaned_response = self._clean_markdown(raw_response)
            
            return cleaned_response
            
        except Exception as e:
            return f"Error generating treatment plan: {str(e)}"
    
    def _create_tpa_eligible_prompt(self, patient_data: Dict[str, Any], scan_data: Dict[str, Any], 
                                   eligibility_result: str) -> str:
        """Create prompt for tPA eligible patients"""
        prompt = f"""
You are a stroke neurologist generating a treatment plan. The text below is context only. NEVER repeat it in your output.

--- PATIENT CONTEXT (DO NOT OUTPUT) ---
Age: {patient_data.get('age', 'N/A')}
Gender: {patient_data.get('gender', 'N/A')}
Time since onset: {patient_data.get('time_since_onset', 'N/A')}
Blood Pressure: {patient_data.get('systolic_bp', 'N/A')}/{patient_data.get('diastolic_bp', 'N/A')} mmHg
Glucose: {patient_data.get('glucose', 'N/A')} mg/dL
INR: {patient_data.get('inr', 'N/A')}
Diagnosis: {scan_data.get('prediction', 'N/A')}
tPA eligibility: {eligibility_result}
---------------------------------------

Return ONLY the treatment plan with clinical actions and follow-up steps. Do not restate patient demographics, history, or eligibility status. No introductions or summaries. Structure the plan with exactly these seven sections and nothing else (all caps headings, plain text underneath):

1. IMMEDIATE INTERVENTIONS (FIRST 24 HOURS)
2. TPA ADMINISTRATION PROTOCOL AND MONITORING
3. POST-TPA CARE AND MONITORING
4. SECONDARY PREVENTION MEASURES
5. REHABILITATION PLANNING
6. FOLLOW-UP SCHEDULE
7. POTENTIAL COMPLICATIONS TO WATCH FOR

Each section must contain actionable items (medications with dose ranges, monitoring frequency, thresholds, referrals, etc.). Avoid bullet symbols like “-” or “•”; instead use short sentences separated by line breaks. Plain text only (no markdown).
        """
        return prompt
    
    def _create_not_eligible_prompt(self, patient_data: Dict[str, Any], scan_data: Dict[str, Any], 
                                   eligibility_result: str) -> str:
        """Create prompt for non-tPA eligible patients"""
        prompt = f"""
You are a stroke neurologist providing a clinical treatment plan. Based on the following patient information, provide ONLY treatment recommendations. Do NOT repeat or summarize the patient information.

Patient Context (for reference only):
- Age: {patient_data.get('age', 'N/A')} years, Gender: {patient_data.get('gender', 'N/A')}
- Time since onset: {patient_data.get('time_since_onset', 'N/A')}
- Blood Pressure: {patient_data.get('systolic_bp', 'N/A')}/{patient_data.get('diastolic_bp', 'N/A')} mmHg
- Glucose: {patient_data.get('glucose', 'N/A')} mg/dL, INR: {patient_data.get('inr', 'N/A')}
- Diagnosis: {scan_data.get('prediction', 'N/A')}
- Not eligible for tPA: {eligibility_result}

This patient is NOT eligible for tPA therapy. Provide a focused alternative treatment plan covering these 7 areas. Be specific, actionable, and evidence-based:

1. IMMEDIATE INTERVENTIONS (First 24 Hours)
   - Supportive care measures
   - Specific medications and dosages
   - Monitoring parameters and frequency
   - Immediate diagnostic tests needed
   - Critical care interventions

2. MEDICAL MANAGEMENT STRATEGIES
   - Alternative thrombolytic options if applicable
   - Antithrombotic therapy
   - Blood pressure management protocol
   - Glucose control measures
   - Other supportive medications

3. SECONDARY PREVENTION MEASURES
   - Antiplatelet/anticoagulant therapy
   - Blood pressure management targets
   - Lipid management
   - Diabetes management if applicable
   - Lifestyle modifications

4. REHABILITATION PLANNING
   - Physical therapy recommendations
   - Occupational therapy needs
   - Speech therapy if indicated
   - Timeline for rehabilitation initiation

5. FOLLOW-UP SCHEDULE
   - Immediate follow-up appointments
   - Specialist referrals needed
   - Imaging follow-up schedule
   - Long-term monitoring plan

6. ALTERNATIVE INTERVENTIONS (If Applicable)
   - Mechanical thrombectomy consideration
   - Other interventional options
   - Surgical interventions if indicated

7. MONITORING PARAMETERS
   - Neurological assessment frequency
   - Vital signs monitoring protocol
   - Laboratory monitoring needs
   - Signs of complications to monitor

IMPORTANT INSTRUCTIONS:
- Provide ONLY treatment recommendations and clinical actions
- Do NOT repeat patient demographics or history
- Use clear section headings in ALL CAPS
- Be specific with dosages, frequencies, and timelines where applicable
- Write in plain text format - NO markdown symbols (#, *, **, etc.)
- Use professional medical terminology
- Keep it concise but comprehensive
        """
        return prompt
    
    def refine_treatment_plan(self, existing_plan: str, physician_notes: str) -> str:
        """
        Refine an existing treatment plan based on physician input using ChatGPT.
        """
        if not self.api_key:
            return "AI service is not configured. Please set OPENAI_API_KEY environment variable."
        
        try:
            prompt = f"""
            Below is an existing treatment plan for a stroke patient:
            
            {existing_plan}
            
            The physician has provided the following additional notes and modifications:
            
            {physician_notes}
            
            Please refine and update the treatment plan incorporating the physician's notes while maintaining medical accuracy and evidence-based recommendations. 
            Highlight any changes made and provide the updated comprehensive treatment plan.
            
            IMPORTANT: Format your response in plain text only. Do NOT use markdown formatting symbols like #, *, **, or bullet points. Write in a professional medical format.
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system", 
                        "content": "You are an expert neurologist. Refine treatment plans based on physician input while maintaining medical accuracy. Provide responses in plain text format without markdown."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                max_tokens=1500,
                temperature=0.3
            )
            
            raw_response = response.choices[0].message.content.strip()
            
            # Clean any markdown that might still be present
            cleaned_response = self._clean_markdown(raw_response)
            
            return cleaned_response
            
        except Exception as e:
            return f"Error refining treatment plan: {str(e)}"

# Global instance - lazy loaded
chatgpt_service = None

def get_chatgpt_service():
    global chatgpt_service
    if chatgpt_service is None:
        chatgpt_service = ChatGPTTreatmentPlanService()
    return chatgpt_service
