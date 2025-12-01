ray@ray-LOQ-15IAX9:~/Projects/25S2-C-NYP-ITI122---Generative-AI-Assignment (simple-db)$ time make explore_llm_single
source $(conda info --base)/etc/profile.d/conda.sh ; conda activate ; conda activate lr &&  python3 explorations/exp_llm_single.py
Experiment with local LLM and single customer lookup tool
Using ollama model gpt-oss:20b
Enter your question (or 'exit' to quit): should i recommend loan to andy or loren
**Recommendation**

| Customer | Residency | Credit Score | Account Status | Overall Risk | Loan Recommendation |
|----------|-----------|--------------|----------------|--------------|---------------------|
| Andy | Non‑resident | 840 | Good‑standing | – | **Do not recommend** |
| Loren | Citizen | 455 | Good‑standing | Medium | **Recommend** |

**Why**

1. **Andy**  
   * **Residency** – Non‑resident customers are explicitly disallowed for loan recommendations.  
   * **Credit Score** – 840 exceeds the policy’s maximum credit score of 674 for a good‑standing account.  
   * **Result** – Both the residency rule and the credit‑score limit prohibit a loan.

2. **Loren**  
   * **Residency** – Citizen, which is allowed.  
   * **Credit Score** – 455 falls between the policy’s minimum (300) and maximum (674) thresholds.  
   * **Account Status** – Good‑standing, matching the policy’s requirement.  
   * **Overall Risk** – Classified as Medium, which is acceptable for a standard loan product.  

**Conclusion**  
Recommend a loan to Loren. Do not recommend a loan to Andy.
Enter your question (or 'exit' to quit): exit

real    1m47.629s
user    0m3.498s
sys     0m0.452s
ray@ray-LOQ-15IAX9:~/Projects/25S2-C-NYP-ITI122---Generative-AI-Assignment (simple-db)$ time make explore_llm_single
source $(conda info --base)/etc/profile.d/conda.sh ; conda activate ; conda activate lr &&  python3 explorations/exp_llm_single.py
Experiment with local LLM and single customer lookup tool
Using ollama model llama3.2:latest
Enter your question (or 'exit' to quit): should i recommend loan to andy or loren
To make a loan recommendation for Andy or Loren, I need to know their credit scores and account status.

However, based on the overall risk policy information provided earlier, if both Andy and Loren have good-standing accounts with high credit scores (above 749), I would recommend a loan to both of them. If either of them has a delinquent account or a low credit score, I would not recommend a loan.

Could you please provide me with the credit scores and account status for both Andy and Loren?
Enter your question (or 'exit' to quit): 