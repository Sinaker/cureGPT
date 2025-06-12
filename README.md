# Doctor Prescription Service

Doctor Prescription Service is a machine learning-based project designed to classify diseases based on a given set of symptoms and provide corresponding prescriptions. The aim is to create an intelligent system that assists doctors and patients by offering accurate diagnoses and treatment suggestions.

## Table of Contents

- [Project Overview](#project-overview)
- [Features](#features)
- [Installation](#installation)
- [Preview](#preview)
- [Data](#data)
- [Model Training](#model-training)
- [Prescription Generation](#prescription-generation)
- [Contribution](#contribution)
- [License](#license)
- [Contact](#contact)

## Project Overview

In this project, we develop a machine learning model to classify diseases based on symptoms provided by the user. Initially, a disease will be predicted, but later on, we are working to also provide prescriptions for the same (possibly using another model).

## Features

- **Symptom-based Disease Classification**: Classifies diseases based on symptoms provided by the user.
- **Prescription Generation**: Provides a list of medications and treatment plans tailored to the diagnosed disease. _(tentative)_
- **Simple Interface**: A simple web interface will be used to allow easy and controlled interaction with the model.
- **User Login**: User login along with chat history is also provided.
- **Docker Scalability**: Containerized deployment with Docker, including NGINX for load balancing and MongoDB containers for efficient data storage and scaling.

## Installation

There are two ways to set up and run the Doctor Prescription Service:

### Manual Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/Sinaker/cureGPT.git
    cd cureGPT
    ```

2. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

3. Create the necessary environment files:
    
    Create a file named `app.env` with the following content:
    ```
    GOOGLE_API_KEY=google_key
    SECRET_KEY=your_secret_key_here
    DB_USERNAME=root
    DB_PASSWORD=example
    ```

4. Run the Flask application:
    ```
    python app.py
    ```
5. The application should now be running and accessible at `http://localhost:8080`.

### Docker Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/yourusername/Doctor-Prescription-Service.git
    cd Doctor-Prescription-Service
    ```

2. Create the necessary environment files:
    
    Create a file named `app.env` with the following content:
    ```
    GOOGLE_API_KEY=google_key
    SECRET_KEY=your_secret_key
    DB_USERNAME=root
    DB_PASSWORD=example
    ```
    
    Create a file named `mongo.env` with the following content:
    ```
    MONGO_INITDB_ROOT_USERNAME=root
    MONGO_INITDB_ROOT_PASSWORD=example
    ```

3. Run with Docker Compose:
    ```bash
    docker-compose up
    ```

The application should now be running and accessible at `http://localhost`.

## Preview

### Signup Page:

![image](https://github.com/user-attachments/assets/52a33f5d-7dc4-4b4c-8901-457770100195)



### Interface After logging in:

![image](https://github.com/user-attachments/assets/47ceed2b-59b7-450d-94ea-f2e4728a1754)



### Prediction:

![image](https://github.com/user-attachments/assets/75759f64-9e08-4aab-a981-2d2fa4cb806b)



### Chat History:

![image](https://github.com/user-attachments/assets/7f4cfe75-3213-48fa-a574-6ea140362dbb)





## Data

The project relies on a dataset containing symptoms and their associated diseases. The dataset has the following:

- **Symptoms**: A list of columns containing symptoms associated with each disease. Each column is a symptom on its own with a binary output: 0 representing that the symptom is not present, and 1 meaning that the symptom is present.
- **Diseases**: A comprehensive list of diseases covered by the model.
- **Prescriptions**: A list of drugs that can be used to help in the treatment process. _(tentative)_

The dataset has around 250,000 rows comprising 339 symptoms with 773 diseases.

## Model Training

The machine learning model is trained using the following steps:

1. **Data Preprocessing**:
    - Clean and preprocess the symptom data.
    - Encode the symptoms and diseases as numerical values.
    
2. **Model Selection**:
    - Currently `RandomForestClassifier` came up as the best suited algorithmn for our use case however we also use:  
        - Logistic Regression
        - Boosting techniques (like Gradient Descent, Histogram Boosting)
    
3. **Training**:
    - Train the selected model on the dataset.
    
4. **Evaluation**:
    - Evaluate the model's accuracy, precision, recall, and other metrics. A comprehensive graph will be provided in the Jupyter notebook.

5. **Optimization**:
    - Optimize hyperparameters using techniques like Grid Search or Randomized Search.

## Prescription Generation

Once a disease is classified, the system generates a prescription (method not decided yet).

## Contribution

This project is jointly contributed to by the members of the DPS Team in Makernova 2.0, a recruitment program for DRISHTI (SVNIT).

## License

This project is licensed under the MIT License.

## Contact

For any inquiries or further information, please reach out via email at:

Kanishk Pandey
Email: kanishkp.dev@gmail.com

Feel free to connect for collaboration, project queries, or access to relevant resources such as API keys.
