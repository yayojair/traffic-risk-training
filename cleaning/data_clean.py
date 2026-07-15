import pandas as pd

class DataCleaner:
    def __init__(self, data: pd.DataFrame):
        self.data = data

    def remove_duplicates_by_id(self):
        """Remove duplicate rows from the DataFrame based on the 'id' column."""
        self.data = self.data.drop_duplicates(subset=['id'])

    def remove_nan_rows(self, columns: list[str]):
        """Remove rows where the specified column has NaN/None values."""
        self.data = self.data.dropna(subset=columns)
  
    def remove_columns(self, columns: list[str]):
        """Remove specified columns from the DataFrame."""
        self.data = self.data.drop(columns=columns, errors="ignore")
        
    def sample_data(self, sampling_quantity):
        self.data = self.data.sample(n=sampling_quantity,random_state=42)
    
    def get_cleaned_data(self) -> pd.DataFrame:
        """Return the cleaned DataFrame."""
        return self.data
    
    

    