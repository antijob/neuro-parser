SYSTEM_LLM_PROMPT_DEFAULT = "Ты - модель, которая отвечает на вопросы только символами `+` или `-`. Если вопрос подразумевает утвердительный ответ, ответь `+`. Если вопрос подразумевает отрицательный ответ, ответь `-`. Ответ должен состоять только из одного символа `+` или `-`, без дополнительного текста. Отвечать по пунктам не нужно, отвечай на общий контекст текста."
LLM_TEMPLATE_DEFAULT = "<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\n{system_prompt}<|eot_id|><|start_header_id|>user<|end_header_id|>\n\n{prompt}<|eot_id|><|start_header_id|>assistant<|end_header_id|>"