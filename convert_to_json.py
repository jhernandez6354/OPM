import json
import csv
def csv_to_json(csv_file_path, json_file_path):
    output_dict=[]
    with open(csv_file_path, "r") as file:
        for line in file:
            if not line.startswith("#"):
                v_int=2
                v_dict=[]
                values = line.strip().split('*')
                
                line_count=len(values[2::])
                while v_int <= line_count:
                    v_dict.append(values[v_int])
                    v_int+=1
                output_dict.append(dict(
                    #id=values[1],
                    type=values[3],
                    level=values[2],
                    #essence=(values[5].split(','))[-1],
                    shards=values[4]
                ))

    with open(json_file_path, 'w', encoding = 'utf-8') as json_file_handler:
        json_file_handler.write(json.dumps(output_dict, indent = 4))

csv_to_json("csv\\HeroLimiterLevel.csv", "convert.json")