import streamlit as st
import csm
import base64
import openai
import requests
import json
import os
import time
from csm import CSMClient
  
# Initialize image_url, session_code and csm_api_key
image_url = ""
session_code = ""
csm_api_key = "CSM_API_KEY"

# Initialize CSM client
csm_client = CSMClient(api_key=csm_api_key)

# Streamlit app
def main():
    global image_url, session_code # declare image_url and session_code as global variables

    st.set_page_config(layout="wide", page_title="AI jewellery design")

    # Ask for OpenAI API key
    openai_api_key = st.text_input("Enter your OpenAI API key:")
    if not openai_api_key:
        st.warning("Please enter your OpenAI API key")
        st.stop()

    # Set OpenAI API key
    openai.api_key = openai_api_key

    st.title("Automated jewellery 3D model design")

    # Step 1: Jewellery Image Prompt Generation
    st.header("Step 1: jewellery image prompt generation")
    user_prompt = st.text_input("Enter your prompt:")
    st.write("- Select styles for your jewellery design:")
    style_options = ["Modern", "Minimalist", "Classic", "Vintage", "Bohemian", "Art Deco", "Gothic", "Ethnic", "Geometric", "Nature-inspired", "Futuristic", "Industrial", "Romantic", "Abstract", "Retro", "Avant-Garde", "Sporty", "Elegant", "Casual", "Eclectic"]
    selected_styles = st.multiselect("Select styles:", style_options, key="style_multiselect")

    # Initialize generated_prompt
    generated_prompt = ""

    combined_prompt = f"{user_prompt} the image must have a white background and the styles should include {', '.join(selected_styles).lower()}"
    
    if st.button("Generate prompt", key="generate_prompt_button"):
        generated_prompt = generate_jewellery_prompt(combined_prompt)
        st.success(f"Generated prompt: {generated_prompt}")

    # Step 2: DALL-E 3 image generation
    st.header("Step 2: DALL-E 3 image generation")
    image_prompt = st.text_input("Generated image prompt:", value=generated_prompt, key="image_prompt")
    custom_image_prompt = st.text_input("Customize image prompt (optional):", key="custom_image_prompt")
    
    if st.button("Generate image", key="generate_image_button"):
        try:
            if custom_image_prompt:
                image_url = generate_image(custom_image_prompt)
            else:
                image_url = generate_image(image_prompt)
            st.image(image_url, caption="Generated image", use_column_width=True)
        except KeyError as e:
            st.error(f"Error: {e}. Please check your image prompt and try again")

    # Step 3: 3D model generation with CSM
    st.header("Step 3: 3D model generation with CSM")
    csm_image_url = st.text_input("Enter image URL for 3D model generation:", value=image_url, key="csm_image_url")

    if st.button("Generate 3D model", key="generate_3d_model_button"):
        if csm_image_url:
            csm_response = generate_3d_model(csm_image_url)
            if csm_response:
                session_code = csm_response.session_code
                if session_code:
                    st.success(f"3D model generation request sent. Session code: {session_code}")
                    st.json(csm_response.__dict__)
                    # Get the local model URL
                    st.info("Checking 3D model generation status...")
                    st.success("3D model generation completed")
                    st.write(f"3D model URL: {csm_response.mesh_path}")
                    if csm_response.mesh_path and os.path.exists(csm_response.mesh_path):
                        # Display the 3D model if the file exists
                        with open(csm_response.mesh_path, 'rb') as file:
                            st.download_button("Download 3D model", file, file_name="mesh.glb")
                        st.subheader("3D model visualization")
                        uploaded_file = st.file_uploader("Upload a 3D model file (e.g., .glb or .gltf)", type=["glb", "gltf"])
                        if uploaded_file:
                            # Save the uploaded file locally
                            file_path = save_uploaded_file(uploaded_file)
                            if file_path:
                                st.success(f"File uploaded successfully! Saved to {file_path}")
                                # Display the uploaded 3D model
                                display_3d_model(file_path)
                            else:
                                st.error("Failed to save the uploaded file")
                        else:
                            st.info("Please upload a 3D model file to get started")
                    else:
                        st.error("3D model file not found")
                else:
                    st.error("Error: session code not found in the response")
            else:
                st.error("Failed to generate 3D model")
        else:
            st.error("Please provide a non-empty image URL for 3D model generation")

# Function to generate jewellery image prompt
def generate_jewellery_prompt(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
    )
    return response["choices"][0]["message"]["content"]

# Function to generate image using DALL-E 3
def generate_image(image_prompt):
    response = openai.Image.create(
        model="dall-e-3",
        prompt=image_prompt,
        size="1024x1024",
        quality="standard",
        n=1,
    )
    image_url = response["data"][0]["url"]
    return image_url

# Function to generate 3D model using CMS Client
def generate_3d_model(image_url):
    try:
        # Use the CSMClient's image_to_3d method with a URL
        result = csm_client.image_to_3d(image_url, generate_spin_video=True, mesh_format='glb')
        return result
    except Exception as e:
        st.error(f"Error generating 3D model: {e}")
        return None


# Function to save uploaded file locally
def save_uploaded_file(uploaded_file):
    file_path = os.path.join("./", uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return file_path

# Function to visualize 3D model in Streamlit using <model-viewer>
def display_3d_model(file_path):
    if file_path and os.path.exists(file_path):
        # Display the 3D model using <model-viewer> component with additional attributes
        st.components.v1.html(f"""
            <model-viewer src="{file_path}"
                alt="3D model" auto-rotate camera-controls
                shadow-intensity="1" exposure="1"
                environment-image="neutral"
                style="width: 100%; height: 100vh; background-color: #F0F0F0;">
            </model-viewer>
            """, height=800)
    else:
        st.error("File not found")

if __name__ == "__main__":
    main()
