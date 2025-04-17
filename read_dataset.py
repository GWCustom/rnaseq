import bfabric_web_apps
import pandas as pd

wrapper = bfabric_web_apps.get_power_user_wrapper({"environment":"test"})

dataset = wrapper.read("dataset", {"id": 57469})

print(dataset)

dataset = dataset[0]

attributes = dataset.get("attribute", []) 
items = [elt.get("field") for elt in dataset.get("item", [])]

position_map = {str(elt.get("position")): elt.get("name") for elt in attributes} # Create a mapping of attribute positions to names
df_dict = {elt : [] for elt in position_map.values()} # Create a dictionary to hold the dataframe data

for item in items: 
    for field in item: 
        attribute_position = field.get("attributeposition")
        df_dict[position_map.get(attribute_position)].append(field.get("value")) # Append the field value to the corresponding attribute name in the dictionary
            
print("df_dict", df_dict)