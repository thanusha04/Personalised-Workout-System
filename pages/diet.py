import streamlit as st
from langchain.chat_models import ChatOpenAI
from langchain import PromptTemplate
from langchain.chains import LLMChain
import openai

# Function to calculate calories and macronutrients
def calculate_calories(weight, height, age, gender, activity_level,veg):
    if gender.lower() == "male":
        bmr = 10 * weight + 6.25 * height - 5 * age + 5
    elif gender.lower() == "female":
        bmr = 10 * weight + 6.25 * height - 5 * age - 161
    else:
        return "Invalid gender. Please specify 'male' or 'female'."

    activity_multiplier = {
        "sedentary": 1.2,
        "light": 1.375,
        "moderate": 1.55,
        "active": 1.725,
        "very active": 1.9
    }
    tdee = bmr * activity_multiplier.get(activity_level.lower(), 1.2)

    protein_calories = 0.3 * tdee
    fat_calories = 0.2 * tdee
    carb_calories = 0.5 * tdee

    protein_grams = protein_calories / 4
    fat_grams = fat_calories / 9
    carb_grams = carb_calories / 4

    return {
        "calories": round(tdee, 2),
        "protein": round(protein_grams, 2),
        "fat": round(fat_grams, 2),
        "carbs": round(carb_grams, 2),
        "veg":veg
    }

# Streamlit UI setup
st.set_page_config(page_title="South Indian Diet Generator", layout="wide")
st.title("South Indian Diet Generator")
st.header("Generate a personalized South Indian diet plan based on your details.")

# Input form for user details
with st.sidebar.form("Diet Details"):
    weight = st.number_input("Weight (kg):", min_value=30.0, max_value=200.0, step=0.1)
    height = st.number_input("Height (cm):", min_value=100.0, max_value=250.0, step=0.1)
    age = st.number_input("Age (years):", min_value=10, max_value=100, step=1)
    gender = st.selectbox("Gender:", ["Male", "Female"])
    veg = st.selectbox("Veg or Non veg:", ["Vegetarian", "Non vegetarian"])
    activity_level = st.selectbox(
        "Activity Level:",
        ["Sedentary", "Light", "Moderate", "Active", "Very Active"]
    )
    submitted = st.form_submit_button("Generate Diet Plan")

# OpenAI API key validation
if "currentkey" not in st.session_state:
    st.session_state.currentkey = ""

try:
    st.session_state.currentkey = st.secrets["open_ai_key"]
except:
    pass

if st.session_state.currentkey:
    openai.api_key = st.session_state.currentkey
else:
    st.sidebar.text_input("Enter OpenAI API Key:", key="input")
    if st.sidebar.button("Validate Key"):
        openai.api_key = st.session_state.input
        st.session_state.currentkey = st.session_state.input

# Generate diet plan if form submitted
if submitted and st.session_state.currentkey:
    macros = calculate_calories(weight, height, age, gender, activity_level,veg)

    # Define prompt template for LangChain
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.5, openai_api_key=st.session_state.currentkey)
    template = """
    Based on the following macronutrient distribution:
    - Calories: {calories} kcal
    - Protein: {protein} g
    - Fat: {fat} g
    - Carbs: {carbs} g

    Create a personalized South Indian diet plan for a day including breakfast, lunch, dinner, and snacks. and the person is a {veg} guy
    """
    prompt = PromptTemplate(
        input_variables=["calories", "protein", "fat", "carbs","veg"],
        template=template
    )
    chain = LLMChain(llm=llm, prompt=prompt)

    # Generate diet plan
    with st.spinner("Generating your diet plan..."):
        diet_plan = chain.run(macros)
        st.subheader("Your South Indian Diet Plan")
        st.write(diet_plan)
else:
    st.header("Enter your details to generate a personalized diet plan!")
