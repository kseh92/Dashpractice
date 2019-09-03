import base64
import io

import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_table

import pandas as pd


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)


ColumnChecklist = dcc.Checklist(
    id='column-checkboxes',
    options=[dict(label='hello', value='world', disabled=True)],
    value=['world']
)

ColumnSubmitButton = html.Button('Submit', id='submit-button')

app.layout = html.Div([
    dcc.Upload(
        id='upload-data',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select Files')
        ]),
        style={
            'width': '100%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
        },
        # Allow multiple files to be uploaded
        multiple=False
    ),
    html.Div(id='output-data-upload'),
    html.Div([ColumnChecklist, ColumnSubmitButton]),
    html.Div(id='check-result'),
])


def parse_contents_for_options(contents, filename, date):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')))
        elif 'xls' in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))
        else:
            raise Exception('unknown extension')
    except Exception:
        return html.Div([
            'There was an error processing this file.'
        ])
    # print([{'name': i, 'id': i} for i in df.columns])


    return [dict(label=col, value=col) for col in df.columns]



def parse_contents(contents, filename, date):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')))
        elif 'xls' in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))
        else:
            raise Exception('unknown extension')
    except Exception:
        return html.Div([
            'There was an error processing this file.'
        ])
    # print([{'name': i, 'id': i} for i in df.columns])

    df2 = pd.DataFrame(df.dtypes).reset_index()
    df2.columns = ['Column', 'Type']

    return html.Div([
        html.H5(filename),
        #html.Div([
        #    ColumnChecklist,
        #    ColumnSubmitButton,
        #]),
        html.Div(dash_table.DataTable(
             data=df2.to_dict('records'),
             columns=[{'name': i, 'id': i} for i in df.columns]
         )),

        html.Hr(),  # horizontal line

        # For debugging, display the raw contents provided by the web browser
        html.Div('Raw Content'),
        html.Pre(contents[0:200] + '...', style={
            'whiteSpace': 'pre-wrap',
            'wordBreak': 'break-all'
        })
    ])


@app.callback(Output('column-checkboxes', 'options'),
              [Input('upload-data', 'contents')],
              [State('upload-data', 'filename'),
               State('upload-data', 'last_modified')])
def update_options(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        option = parse_contents_for_options(list_of_contents, list_of_names, list_of_dates)
        return option


@app.callback(Output('output-data-upload', 'children'),
              [Input('upload-data', 'contents')],
              [State('upload-data', 'filename'),
               State('upload-data', 'last_modified')])
def update_output(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        return parse_contents(list_of_contents, list_of_names, list_of_dates)
        # children = [
        #     parse_contents(c, n, d) for c, n, d in
        #     zip(list_of_contents, list_of_names, list_of_dates)]
        # return children


@app.callback(Output('check-result', 'children'),
              [Input('submit-button', 'n_clicks')],
              [State('column-checkboxes', 'value')])
def forward_to_next_step(*args):
    print(args)
    return html.Div('helloworld')


if __name__ == '__main__':
    app.run_server(debug=True)