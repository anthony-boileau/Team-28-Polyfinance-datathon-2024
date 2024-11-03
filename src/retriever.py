import transformer
class Retriever:
    def __init__(self):
        # You can initialize any attributes here, like database connection parameters if needed.
        pass

    def get_context(self, query):
        # Replace this with the actual logic to retrieve data from the database
        data = 'Old Apple CEO Steve Jobs dead, Guillaume now new CEO'  # Get data from DB based on the query

        context = (
            "Act as a financial analyst who reviews annual reports,"
            "summarizes key insights, and answers specific questions about financial "
            "metrics and company performance very concisely based on the following text: \n"
            f"{data}"
            "\n Answer without talking to the first person."
        )
        return context



        

