# 📚 Digital Library Catalogue Dashboard

Welcome to the **Digital Library Catalogue Dashboard**, an interactive analytical tool designed for librarians, researchers, and book enthusiasts to explore a vast collection of books.

This dashboard visualizes the `final_catalogue_cleaned.csv` dataset, offering insights into publication trends, author contributions, and language distribution across the collection.

## 🚀 Features

### 📊 Interactive Dashboard
- **KPI Metrics**: Instantly view Total Books, Unique Authors, and the Most Common Language in the filtered selection.
- **Top Authors**: Visualize the most prolific authors via a horizontal bar chart.
- **Publication Trends**: Analyze how book publications have evolved over time with an area chart.
- **Language Distribution**: See the breakdown of books by language in a donut chart.

### 🔎 Data Explorer
- **Searchable Database**: Quickly find books by title using the search bar.
- **Detailed Table**: View the full catalogue with sorting and filtering capabilities.
- **Dynamic Content**: All tables and charts update in real-time based on your filters.

### 🎛️ Advanced Filtering
- **Sidebar Controls**: Filter the entire dataset by:
  - **Language**: Select one or multiple languages.
  - **Category**: Filter by genre or category.
  - **Author**: Narrow down to specific authors.
  - **Publication Year**: Use the range slider to focus on a specific time period.

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.8 or higher
- [Streamlit](https://streamlit.io/)

### 1. Clone the Repository
```bash
git clone <repository-url>
cd Streamlit_Telugu_Catalogue
```

### 2. Install Dependencies
Install the required Python packages using pip:
```bash
pip install -r requirements.txt
```

### 3. Run the Application
Start the Streamlit server:
```bash
streamlit run app.py
```

The dashboard will open automatically in your default web browser (usually at `http://localhost:8501`).

## 📂 Project Structure
- `app.py`: The main application script containing the UI logic and data visualization code.
- `requirements.txt`: List of Python dependencies.
- `final_catalogue_cleaned.csv.csv`: The source dataset (ensure this file is in the root directory).

## 💡 Notes
- The application handles missing data (e.g., unknown years or authors) gracefully to ensure a smooth user experience.
- The UI is optimized for wide screens to visualize data effectively.
