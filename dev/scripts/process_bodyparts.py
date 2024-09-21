import yaml
import pandas as pd
import os
import re
import argparse

# Function to convert YAML data to CSV
def yaml_to_csv(yaml_file, output_folder):
    # Load the YAML file
    with open(yaml_file, "r") as file:
        data_dict = yaml.safe_load(file)

    # Extract body_parts section and concatenate if there are other sections
    entries = []
    if 'body_parts' in data_dict:
        entries.extend(data_dict['body_parts'])
    
    # Determine the max number of abilities in any entry
    max_abilities = max(len(entry.get("abilities", [])) for entry in entries)
    
    # Create a list for CSV rows
    csv_data = []
    
    for entry in entries:
        row = {
            "title": entry.get("title", ""),
            "system": entry.get("system", ""),
            "description": entry.get("description", "")
        }
        # Add abilities columns
        for i, ability in enumerate(entry.get("abilities", []), 1):
            row[f"ability{i}"] = ability
        
        csv_data.append(row)
    
    # Convert to a DataFrame
    df = pd.DataFrame(csv_data)
    
    # Ensure all ability columns are present up to max_abilities
    for i in range(1, max_abilities + 1):
        if f"ability{i}" not in df.columns:
            df[f"ability{i}"] = ""
    
    # Create output CSV file path
    yaml_filename = os.path.basename(yaml_file).replace(".yaml", "").replace(".yml", "")
    output_csv = os.path.join(output_folder, f"{yaml_filename}_output.csv")
    
    # Write to CSV
    df.to_csv(output_csv, index=False)
    print(f"Data successfully written to {output_csv}")
    
    return entries

# Function to generate a text report
def generate_report(entries, output_folder, yaml_file):
    # Initialize dictionaries to store system stats and various condition stats
    total_body_parts = len(entries)
    ability_stats = {}
    system_stats = {}
    condition_stats = {"granted": {}, "ignored": {}}
    injury_stats = {
        "additional_injury": [],
        "physical_injury": [],
        "internal_injury": [],
        "severed_injury": [],
        "obliterated_injury": []
    }

    for entry in entries:
        system = entry.get("system", "Unknown")
        title = entry.get("title", "Unnamed Body Part")
        
        # Add the title to the appropriate system category
        if system in system_stats:
            system_stats[system].append(title)
        else:
            system_stats[system] = [title]
        
        # Get stats based of abilities
        abilities = entry.get("abilities", [])
        num_of_abilities = len(abilities)
        if num_of_abilities in ability_stats:
            ability_stats[num_of_abilities].append(title)
        else:
            ability_stats[num_of_abilities] = [title]

        for ability in abilities:
            ability = ability.lower()
            # Determine if the ability grants or ignores the condition
            grants_condition = "ignore" not in ability
            match = re.search(r'(\w+)\s+condition', ability, re.IGNORECASE)
            if match:
                condition_type = match.group(1)
                if grants_condition:
                    if condition_type in condition_stats["granted"]:
                        condition_stats["granted"][condition_type].append(title)
                    else:
                        condition_stats["granted"][condition_type] = [title]
                else:
                    if condition_type in condition_stats["ignored"]:
                        condition_stats["ignored"][condition_type].append(title)
                    else:
                        condition_stats["ignored"][condition_type] = [title]


            # Check for physical injury
            if re.search(r'physical injury', ability, re.IGNORECASE) and re.search(r'deal', ability, re.IGNORECASE):
                injury_stats["physical_injury"].append(title)

            # Check for internal injury
            if re.search(r'internal injury', ability, re.IGNORECASE) and re.search(r'deal', ability, re.IGNORECASE):
                injury_stats["internal_injury"].append(title)

            # Check for severed injury
            if re.search(r'injury', ability, re.IGNORECASE) and re.search(r'severed', ability, re.IGNORECASE):
                injury_stats["severed_injury"].append(title)

            # Check for obliterated injury
            if re.search(r'injury', ability, re.IGNORECASE) and re.search(r'obliterated', ability, re.IGNORECASE):
                injury_stats["obliterated_injury"].append(title)
            
            # Check for additional injury keyword
            if re.search(r'additional injur', ability, re.IGNORECASE):
                injury_stats["additional_injury"].append(title)

    # Create report content
    report_content = []
    report_content.append(f"Report for YAML file: {yaml_file}\n")
    report_content.append("=================================\n\n")
    
    # Ability Counts
    report_content.append(f"Total Number of Body Parts: {total_body_parts}\n")
    report_content.append("Ability Statistics:\n")
    for num, body_parts in ability_stats.items():
        report_content.append(f"Body Parts With {num} Abilities: ")
        report_content.append(f"Number of Body Parts: {len(body_parts)}")
        for part in body_parts:
            report_content.append(f" - {part}")
        report_content.append("\n")
    # System statistics report
    report_content.append("System Statistics:\n")
    for system, body_parts in system_stats.items():
        report_content.append(f"Body Parts With System {system}: ")
        report_content.append(f"Number of Body Parts: {len(body_parts)}")
        for part in body_parts:
            report_content.append(f" - {part}")
        report_content.append("\n")
    
    # Condition statistics report
    report_content.append("Condition Statistics:\n")
    total_granted_condition_parts = sum(len(parts) for parts in condition_stats["granted"].values())
    total_ignored_condition_parts = sum(len(parts) for parts in condition_stats["ignored"].values())
    
    report_content.append(f"Total Body Parts Granting a Condition: {total_granted_condition_parts}\n")
    for condition_type, body_parts in condition_stats["granted"].items():
        report_content.append(f"Condition Type (Granted): {condition_type}")
        report_content.append(f"Number of Body Parts: {len(body_parts)}")
        for part in body_parts:
            report_content.append(f" - {part}")
        report_content.append("\n")
    
    report_content.append(f"Total Body Parts Ignoring a Condition: {total_ignored_condition_parts}\n")
    for condition_type, body_parts in condition_stats["ignored"].items():
        report_content.append(f"Condition Type (Ignored): {condition_type}")
        report_content.append(f"Number of Body Parts: {len(body_parts)}")
        for part in body_parts:
            report_content.append(f" - {part}")
        report_content.append("\n")
    
    # Injury statistics report
    report_content.append("Injury Statistics:\n")
    
    # Physical Injury
    report_content.append(f"Body Parts that Deal Physical Injury: {len(injury_stats['physical_injury'])}")
    for part in injury_stats["physical_injury"]:
        report_content.append(f" - {part}")
    report_content.append("\n")
    
    # Internal Injury
    report_content.append(f"Body Parts that Deal Internal Injury: {len(injury_stats['internal_injury'])}")
    for part in injury_stats["internal_injury"]:
        report_content.append(f" - {part}")
    report_content.append("\n")
    
    # Severed Injury
    report_content.append(f"Body Parts that can Sever: {len(injury_stats['severed_injury'])}")
    for part in injury_stats["severed_injury"]:
        report_content.append(f" - {part}")
    report_content.append("\n")
    
    # Obliterated Injury
    report_content.append(f"Body Parts that can Obliterate: {len(injury_stats['obliterated_injury'])}")
    for part in injury_stats["obliterated_injury"]:
        report_content.append(f" - {part}")
    report_content.append("\n")

    # Additional Injury
    report_content.append(f"Body Parts That Deal 1 Additional Injury: {len(injury_stats['additional_injury'])}")
    for part in injury_stats["additional_injury"]:
        report_content.append(f" - {part}")
    report_content.append("\n")
    
    # Create the output report file
    yaml_filename = os.path.basename(yaml_file).replace(".yaml", "").replace(".yml", "")
    output_report = os.path.join(output_folder, f"{yaml_filename}_report.txt")
    
    # Write the report to a text file
    try:
        with open(output_report, "w") as report_file:
            report_file.write("\n".join(report_content))
        print(f"Report successfully written to {output_report}")
    except IOError as e:
        print(f"An error occurred while writing the report: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert YAML file to CSV and generate a system report.")
    parser.add_argument("yaml_file", help="Path to the input YAML file")
    parser.add_argument("output_folder", help="Path to the folder where the CSV and report should be saved")
    
    args = parser.parse_args()
    
    # Ensure output folder exists
    if not os.path.exists(args.output_folder):
        os.makedirs(args.output_folder)
    
    # Run the conversion to CSV and return the entries
    entries = yaml_to_csv(args.yaml_file, args.output_folder)
    
    # Generate a report based on the processed entries
    generate_report(entries, args.output_folder, args.yaml_file)
