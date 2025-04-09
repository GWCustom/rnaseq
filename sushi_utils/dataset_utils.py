import pandas as pd

def dataset_to_dictionary(dataset): 

    """
    Convert B-Fabric API Dataset Response 
    to a pandas dataframe

    Args: 
        dataset (dict): B-Fabric API Dataset Response

    Returns:
        pd.DataFrame: Dataframe containing the dataset information
    """

    # Check if the dataset is empty
    if not dataset:
        return pd.DataFrame()

    attributes = dataset.get("attribute", []) 
    items = [elt.get("field") for elt in dataset.get("item", [])]

    position_map = {str(elt.get("position")): elt.get("name") for elt in attributes} # Create a mapping of attribute positions to names
    df_dict = {elt : [] for elt in position_map.values()} # Create a dictionary to hold the dataframe data

    for item in items: 
        for field in item: 
            attribute_position = field.get("attributeposition")
            df_dict[position_map.get(attribute_position)].append(field.get("value")) # Append the field value to the corresponding attribute name in the dictionary
                
    # Create a dataframe from the dictionary
    return df_dict

def dataset_dict_to_tsv(): 
    return