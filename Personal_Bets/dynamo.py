import boto3
import pandas as pd


class MyBets:
    def __init__(self):
        # set up dynamo db info
        self.db = boto3.resource('dynamodb')
        self.table = self.db.Table('MyBets')

    def _load_table_data(self):
        return self.table.scan()['Items']

    def _load_local_data(self):
        self.local_data_csv_name = "Dillon_Current.csv"
        self.local_data = pd.read_csv(self.local_data_csv_name)
        self.local_data.fillna(value="NULL", inplace=True)

        # cols var
        self.cols = [col for col in list(self.local_data.columns) if 'Unnamed' not in col]

    def _row_to_dict_item(self, row):
        new_item = {col: str(row[col]) for col in self.cols}
        return new_item

    def insert_row_to_table(self, row):
        new_item = self._row_to_dict_item(row)
        self.table.put_item(
            Item=new_item
        )
        print('item added!')

    def _delete_item(self, item_espn_id):
        self.table.delete_item(
            Key={'ESPN_ID': item_espn_id}
        )
        print('item deleted!')

    def _is_row_in_table(self, row):
        data = self._load_table_data()
        row_item = self._row_to_dict_item(row)
        row_in_table = False
        for record in data:
            if record == row_item:
                row_in_table = True
                break

        return row_in_table

    def add_new_items_to_table(self):
        num_local_rows = len(self.local_data) - 1
        for i in range(num_local_rows):
            current_local_row = self.local_data.iloc[i, :]
            local_row_in_table = self._is_row_in_table(current_local_row)
            if not local_row_in_table:
                self.insert_row_to_table(current_local_row)

        new_table_data = self._load_table_data()

        assert len(self.local_data) == len(new_table_data)


if __name__ == "__main__":
    x = MyBets()
    x._load_local_data()


"""
data = pd.read_csv("Dillon_Current.csv")
cols = [col for col in list(data.columns) if 'Unnamed' not in col]


def row_to_dict(row):
    new_item = {col: row[col] for col in cols}
    return new_item


def insert_item(table, item):
    db = boto3.resource('dynamodb')
    table = db.


#########################################################################
import boto3

# client = boto3.client('dynamodb',aws_access_key_id='AKIA4EWC6AWZVDF4JFOF', aws_secret_access_key='xxxx', region_name='***')


db = boto3.resource('dynamodb')
table = db.Table('employees')

# table.put_item(
#     Item={
#         'emp_id': "3",
#         'name': "Dillon",
#         'Age': "24"
#     }
# )

response = table.get_item(
    Key={"emp_id": "1"}
)
print(response)


response2 = table.delete_item(
    Key={"emp_id": "2"}
)


client = boto3.client("dynamodb")
response3 = client.describe_table(TableName="employees")

# Query

from boto3.dynamodb.conditions import Key
response = table.query(
    KeyConditionExpression=Key('emp_id').eq('1')
)

print(response)


# all data
from boto3.dynamodb.conditions import Attr
data = table.scan()


print(data)
"""
