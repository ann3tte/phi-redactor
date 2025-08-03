## **PHI Redactor: De-identification & Re-identification Tool**  

A **Python-based tool** designed to **automatically remove and restore Protected Health Information (PHI)** from medical records using **Regex**.  

This app is built with **Streamlit** for a simple interface, allowing users to upload medical text files, de-identify them by redacting sensitive information, and later re-identify them by restoring original content using saved mappings.  

---  

## **Features**  
- Regex-Based Detection
- Streamlit Web UI: Simple interface that allows users to upload a single .txt file, view the redacted output directly in-browser​.
- PHI Categories Covered: Covers all 18 HIPAA identifiers.
- Download both deidentified and reidentified files.

---  

## **⚠️ Important: Python Version Compatibility**  

This tool requires Python 3.11 or lower due to compatibility issues with some dependencies. If you're using Python 3.12 or higher, you might encounter installation issues.  

#### ✅ Recommended:  
**Use Python 3.11** for setup.

#### 🔍 **Check Your Python Version:**  
- **Windows:**  
  ```bash
  py -0
  ```  
- **Mac/Linux:**  
  ```bash
  python3 --version
  ```  

---  

## **🛠 Setup & Installation**  

### **1️⃣ Clone the Repository**  
```bash
git clone https://github.com/jemimah-reji/phi-redactor.git
cd phi-redactor
```  

### **2️⃣ Create a Virtual Environment**  
To isolate dependencies and avoid conflicts:  
```bash
python3 -m venv venv
```
Activate the virtual environment:  
- **Mac/Linux**:  
  ```bash
  source venv/bin/activate
  ```  
- **Windows (CMD/PowerShell)**:  
  ```bash
  venv\Scripts\activate
  ```

---

### **3️⃣ Install Dependencies**  
After activating the virtual environment, install the required Python packages:  
```bash
pip install --upgrade pip  # Ensure pip is up to date
pip install -r requirements.txt  # Install dependencies
```

---

### **4️⃣ Generate a Fernet Key for Encryption**  
This tool uses encryption to protect mappings between redacted and original PHI. You need to generate a secret Fernet key for encryption/decryption:

1. **Generate the key**:  
   Run this Python script to generate your key and save it to the `.env` file:
   ```python
   from cryptography.fernet import Fernet

   # Generate the key
   key = Fernet.generate_key()

   # Print the key (copy it for the next step)
   print(key.decode())
   ```

2. **Store the key**:  
   Copy the printed key and save it in a `.env` file in your project’s root directory:
   ```
   FERNET_KEY="your-generated-key-here"
   ```

3. **Add `.env` to your `.gitignore`**  
   Make sure the `.env` file is **never** committed to version control:
   ```plaintext
   .env
   ```

### **5️⃣ Run the Application**  
Start the **Streamlit web app** with the following command:  
```bash
streamlit run app.py
```
This will open the **PHI Redactor** tool in your browser, where you can upload files and start de-identifying/re-identifying.

---

## **📂 Project Structure**
```
📁 deidentify-tool
│── 📄 app.py               # Streamlit UI for file upload & processing
│── 📄 deidentifier.py      # Python script for de-identification (Regex)
│── 📄 reidentifier.py      # Python script for re-identification (restore PHI)
│── 📄 requirements.txt     # List of dependencies
│── 📄 .env                 # Store your Fernet key here (DO NOT COMMIT)
```

---

## **🤝 Contributing**  
If you'd like to improve the project, follow these steps:  

1. **Fork the repository**  
2. **Create a new branch for your changes**  
   ```bash
   git checkout -b feature-branch-name
   ```
3. **Make changes and commit them**  
   ```bash
   git add .
   git commit -m "Added new feature"
   git push origin feature-branch-name
   ```
4. **Create a Pull Request on GitHub**  

---