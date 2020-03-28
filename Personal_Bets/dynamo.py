import boto3
import pandas as pd


class MyBets:
    def __init__(self):
        # set up dynamo db info
        self.db = boto3.resource('dynamodb')
        self.table = self.db.Table('MyBets')

    def _load_local_data(self):
        self.local_data_csv_name = "Dillon_Current.csv"
        self.local_data = pd.read_csv(self.local_data_csv_name)
        self.local_data.fillna(value="NULL", inplace=True)

        # cols var
        self.cols = [col for col in list(self.local_data.columns) if 'Unnamed' not in col]

    def _row_to_dict_item(self, row):
        new_item = {col: row[col] for col in self.cols}
        return new_item

    def insert_row_to_table(self, row):
        new_item = self._row_to_dict_item(row)
        self.table.put_item(
            Item=new_item
        )
        print('item added!')


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
