import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

class VulnerabilityScanner:
    """
    Worker Agent: Specialized in detecting security vulnerabilities.
    """
    def __init__(self, model):
        self.model = model

    def scan(self, code_snippet):
        """
        Analyzes the code snippet and returns a JSON vulnerability report.
        """
        prompt = f"""
        You are an SAP BTP Security Expert and Code Auditor.
        Your task is to analyze the following code snippet (which may be Python, CAP/Node.js, or Java) for security vulnerabilities.
        
        Focus on SAP BTP and General Security Best Practices:
        1.  **SAP Specific**:
            - Hardcoded credentials in `xs-security.json` or `mta.yaml`.
            - Hardcoded service keys or destination credentials.
            - Improper usage of SAP Cloud SDK.
            - Missing role checks (XSUAA) in CAP services.
        2.  **General OWASP**:
            - SQL Injection (CDS injection in CAP).
            - XSS.
            - Insecure Deserialization.
            - Path Traversal.

        Code Snippet:
        ```
        {code_snippet}
        ```

        Output Format:
        You must output strictly VALID JSON. Do not include markdown formatting (like ```json).
        The JSON structure must be:
        {{
            "vulnerabilities": [
                {{
                    "type": "Vulnerability Name",
                    "severity": "High" | "Medium" | "Low",
                    "line": <line_number>,
                    "description": "Brief explanation of the flaw and why it matters in SAP context (if applicable)."
                }}
            ],
            "risk_score": <integer_0_to_100>,
            "risk_score_deviation": "Brief explanation of why points were deducted (e.g., '2 High Severity flaws detected').",
            "summary": "Executive summary of safety status."
        }}

        Risk Score Calculation:
        - Start at 100.
        - High severity = -20 points
        - Medium severity = -10 points
        - Low severity = -5 points
        - Minimum score is 0.
        
        If no vulnerabilities are found, return empty list, score 100, and deviation "No issues found".
        """
        response = self.model.generate_content(prompt)
        text_response = response.text.strip()
        
        # Clean up markdown if model outputs it
        if text_response.startswith("```json"):
            text_response = text_response[7:]
        if text_response.startswith("```"):
            text_response = text_response[3:]
        if text_response.endswith("```"):
            text_response = text_response[:-3]
            
        return text_response.strip()

class SecureRefactorer:
    """
    Worker Agent: Specialized in fixing security vulnerabilities safely.
    """
    def __init__(self, model):
        self.model = model

    def refactor(self, code_snippet, analysis_json):
        """
        Generates a secure version of the code.
        """
        prompt = f"""
        You are a Refactoring Agent, not a Feature Agent.
        
        **Guardrails & Safety Instructions**:
        1.  **Do No Harm**: You must strictly preserve the input/output contract of the function.
        2.  **No Side Effects**: Do not alter business logic or introduce new features. Only fix the security flaws.
        3.  **Sanitization**: You may change how data is handled (e.g., paramerterization, environment variables) to secure it.

        Original Code:
        ```
        {code_snippet}
        ```

        Analysis (JSON):
        {analysis_json}

        Task:
        Rewrite the code to fix all identified vulnerabilities using SAP BTP best practices.
        
        Output Format:
        You must output strictly VALID JSON. Do not include markdown formatting.
        {{
            "fixed_code": "The complete, compilable fixed code block as a string. Escape newlines properly."
        }}
        """
        response = self.model.generate_content(prompt)
        text_response = response.text.strip()
        
        # Clean up markdown if model outputs it
        if text_response.startswith("```json"):
            text_response = text_response[7:]
        if text_response.startswith("```"):
            text_response = text_response[3:]
        if text_response.endswith("```"):
            text_response = text_response[:-3]

        try:
            data = json.loads(text_response.strip())
            return data.get("fixed_code", code_snippet) # Fallback to original if key missing
        except json.JSONDecodeError:
            print(f"DEBUG: Failed to parse JSON: {text_response}")
            # Fallback - sometimes the model just outputs the code
            return text_response

class SecurityOrchestrator:
    """
    Orchestrator Agent: Manages the workflow between Scanner and Refactorer.
    """
    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-001')
        
        # Instantiate Worker Agents
        self.scanner = VulnerabilityScanner(self.model)
        self.refactorer = SecureRefactorer(self.model)

    def analyze_code(self, code_snippet):
        """
        Delegates analysis to the VulnerabilityScanner.
        """
        return self.scanner.scan(code_snippet)

    def fix_code(self, code_snippet, analysis_json):
        """
        Delegates fixing to the SecureRefactorer.
        """
        return self.refactorer.refactor(code_snippet, analysis_json)
