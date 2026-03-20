if st.button("Generate 5 MCQs"):
    if news_input:
        with st.spinner("Setting the paper..."):

            prompt = f"""
            Act as an RBI Assistant examiner.

            Based on the following news, create 5 MCQs for the {topic} section.

            News:
            {news_input}

            Instructions:
            - 5 options (A–E)
            - Give answer + explanation
            - Exam-level difficulty
            """

            try:
                response = model.generate_content(
                    prompt,
                    generation_config={
                        "temperature": 0.7,
                        "max_output_tokens": 1000
                    }
                )
                st.markdown(response.text)

            except Exception as e:
                st.error(f"Error: {str(e)}")
    else:
        st.warning("Please paste some news first!")
