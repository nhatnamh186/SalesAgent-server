from google import genai
from langchain.prompts import PromptTemplate
class OutreachMessageGenerator:
    """
    A class that uses a generative model to create personalized outreach messages
    based on LinkedIn profile details.
    """
    def __init__(self, api_key, model_name="gemini-2.0-flash"):
        """
        Initialize the outreach message generator with an API key and model.
        """
        self.client = genai.Client(api_key=api_key)
        self.model_name = model_name
        self.prompt_template = PromptTemplate(
            input_variables=["fullName", "jobTitle", "companyName", "description", "additional_context", "writing_style"],
            template="""
            You are an expert in professional networking and personalized outreach.
            Your task is to analyze a LinkedIn profile and draft a compelling outreach message
            that feels natural, engaging, and relevant to the recipient's background.

            ### LinkedIn Profile Details:
            - **Full Name:** {fullName}
            - **Job Title:** {jobTitle}
            - **Company Name:** {companyName}
            - **Description of Company:** {description}

            ### Additional Context:
            {additional_context}

            ### Writing Style:
            {writing_style}

            ### Message Requirements:
            - less than 300 characters
            - Not Subject title, only a line
            - Start with a friendly and professional greeting.
            - Acknowledge the recipient’s background and expertise.
            - Express a relevant reason for connecting.
            - Keep the message concise, around 3-5 sentences.
            - End with a clear next step or call to action.

            ### Instructions:
            - Do not preface your message with phrases like "Okay, here's the LinkedIn connection request message."
            - Provide only the outreach message in plain text, without any introductory statements.
            - Ensure the message is friendly, professional, and relevant, acknowledging the recipient's background and providing a clear reason for connecting.
            """
                    )

    def generate_message(self, fullName, jobTitle, companyName, description, additional_context="", writing_style=""):
        """
        Generate a personalized LinkedIn outreach message.
        """
        prompt = self.prompt_template.format(
            fullName=fullName,
            jobTitle=jobTitle,
            companyName=companyName,
            description=description,
            additional_context=additional_context,
            writing_style=writing_style
        )
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=[prompt]
        )
        return response.text.strip()
class SolarPanelDetector:
    """
    A class to detect the presence of solar panels on the rooftop of a factory
    from satellite imagery using a generative AI model.
    """
    def __init__(self, api_key, model_name="gemini-2.0-flash"):
        """
        Initialize the detector with the Gemini API key and model name.

        Args:
            api_key (str): Your Google GenAI API key.
            model_name (str): The name of the Gemini model to use.
        """
        self.client = genai.Client(api_key=api_key)
        self.model_name = model_name

    def check_solar_panel(self, image_path):
        """
        Analyze a satellite image to determine if solar panels are present on a factory rooftop
        near the marked red point.

        Args:
            image_path (str): Path to the image file (satellite photo with a red mark).

        Returns:
            str: "Yes" if solar panels are detected, "No" otherwise.
        """
        prompt = '''
        You are an expert in solar panel detection. Analyze the image and determine if there are any solar panels on rooftop of a factory at the mark point.
        You will give a input that is a satellite image of a factory with a red mark point.
        The satellite image maybe contain other objects such as anothoer factory, house, tree, etc.
        You must dymanic to indentify the rooftop of the factory and analyze it to determine if there are solar panels on it.
        You must follow these rules:
            - Detect the a factory at that red mark location. The factory maybe in here or nearby.
            - Analyze the rooftop of this factory to identify if there are solar panels. A solar panel, 
              also known as a photovoltaic (PV) panel, is a device that converts sunlight into electricity. 
              It's made up of individual solar cells arranged in a panel to maximize electricity generation. 
              Solar panels are a key component of photovoltaic systems, often used for residential, commercial, and industrial power generation, as well as in remote locations. 
              Function:Solar panels harness the sun's energy (photons) and convert it into direct current (DC) electricity. 
              Construction:They are primarily composed of solar cells, which are typically made from silicon or other semiconductor materials. 
              Operation:When sunlight strikes the solar cells, it excites electrons, causing them to flow and produce a current. 
              Arrangement:Solar panels are often arranged in arrays or systems to generate larger amounts of electricity. 
            - Only Return Yes/No. Do not provide any additional information or context.
        Note that:
            - Some objects that can be mistaken for solar panels:
                + Glass windows
                + Roads with lines
                + Corrugated iron roofs
            - Some characteristics that differentiate glass windows from solar panels, such as:
                + Spacing: The gaps between the individual panes are more significant than what is typically seen between solar panels in an array.
                + Reflectivity: While both can be reflective, the nature of the reflection in the image looks more like that of glass.
                + Uniformity: Although they appear somewhat uniform, there are subtle variations and breaks that are less common in tightly packed solar panel installations.
        Your output must be:
            - Yes: If there are solar panels on the rooftop of the factory.
            - No: If there are no solar panels on the rooftop of the factory.
            - Only return Yes/No.'''
        myfile = self.client.files.upload(file=image_path)
        response = self.client.models.generate_content(
            model = self.model_name,
            contents=[myfile, prompt]
        )
        return response.text.strip()

