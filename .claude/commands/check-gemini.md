Run a health check on the Gemini integration.

Do the following:
1. Read backend/app/services/gemini_service.py
2. Check: is JSON parsing handling markdown code fences (```json ... ```)? 
3. Check: is there a timeout set on the Gemini call?
4. Check: is confidence score validated (0.0 to 1.0 range)?
5. Check: what happens if Gemini returns unexpected format?
6. Make any fixes needed directly in gemini_service.py
7. Report what was fixed and what was already correct
