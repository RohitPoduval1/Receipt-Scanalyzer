from ollama import chat


def classify(item: str) -> str:
    """
    Given an item from the receipt, classify it as "Healthy", "Unhealthy", or "Unknown"

    Args:
        items: the food item to classify
    Returns:
        "Healthy", "Unhealthy", or "Unknown"
    """
    preprompt = """
    Background: I am working on an add on to a project that I am working on. I scan in receipts and I will use AI Chat
    like you to classify foods on the receipt as healthy or unhealthy to see if I adhere to the 80% healthy 20% less healthy rule. 

    The Task: I will give you a name from a receipt and you classify it as "Healthy", "Unhealthy", or "Unknown".
    Assume that the food is consumed in moderation and NOT in excess. For example, eggs are healthy but less so when consumed in excess.
    Some foods like Oreos are just straight up not good for you, so they are Unhealthy regardless.
    Brands like Keebler are KNOWN to produce unhealthy sweet foods so if Keebler is provided, it is unhealthy. 

    - “Healthy" means the food is generally nutritious and beneficial for overall health. 
    - "Unhealthy" means the food is high in calories, sugar, salt, unhealthy fats, or is processed and is detrimental to health.
    A doctor would frown upon consuming this. These foods are often highly palatable and produce dopamine spikes. 
    - “Unknown” means you are not familiar with the specific brand or absolutely do not recognize the food so do not bother guessing.
    “Unknown” can also be used if the brand or name sells both healthy and unhealthy food and the name does not distinguish between them.
    Unknown should be used when you do not recognize the brand and are unable to extrapolate. Do not rely heavily on this.

    A note on the input, case does not matter so MILK is the same as Milk is the same as milk.
    Names may be prefixed with abbreviations such as GG for Good and Gather.
    If you can extract a product from these names, do so and judge based on that. 

    Take your time in examining and RE-EXAMINING and reasoning based on the names as some may be incomplete (missing letters or vowels)
    or abbreviations. Respond in this case based on the food name or brand name the provided name is most similar to.
    HIDDEN VLLEY would be most similar to HIDDEN VALLEY so respond based on HIDDEN VALLEY.
    Input will be only brands or food, nothing more. Respond only with “Healthy”, “Unhealthy” or “Unknown”, no explanation or nuance is needed.
    I believe in you and together we can make this project amazing!
    """

    ollama_response = chat(model='llama3.2', messages=[
       {
         'role': 'system',
         'content': preprompt,
       },
       {
         'role': 'user',
         'content': item,
       },
    ])

    return ollama_response['message']['content']
