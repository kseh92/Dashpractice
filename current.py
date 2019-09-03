import base64
import datetime
import io

import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_table

import numpy as np
import pandas as pd
from django_plotly_dash import DjangoDash

import sklearn

external_stylesheets = [
    "https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css",
    'https://codepen.io/chriddyp/pen/bWLwgP.css'
]

if __name__ == "__main__":
    app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
else:
    app = DjangoDash('SimpleExample1', external_stylesheets=external_stylesheets)

# y컬럼 선택을 위한 component
ColumnSelector = dcc.Dropdown(
    id='column-selector', options=[dict(label='hello', value='world')])

# x컬럼 선택을 위한 component
ColumnChecklist = dcc.Checklist(
    id='column-checkboxes',
    options=[
        # dict(
        #     label='hello',
        #     value='world',
        #     disabled=True
        # )
    ],
    # value=['world']
)

ColumnSubmitButton = html.Button('완료', id='submit-button', className='btn btn-primary')

# dash-app-layout
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
    html.Hr(),
    # callback선언을 위해서는 이쪽에 기본적으로 모든 component를 배치해야 합니다.
    # 파일을 올리면 동적으로 그려주고, 해당 element에 callback을 걸고 싶은데,
    # callback처리대상은 미리 모두 선언해두어야 한다고 합니다.
    # https://community.plot.ly/t/dynamic-controls-and-dynamic-output-components/5519
    html.Div(
        [
            html.H6('x:'),
            ColumnChecklist,
            html.H6('y:'),
            ColumnSelector,
            html.Hr(),
            html.P('x값과 y값을 선택하고 완료버튼을 누르세요.'),
            ColumnSubmitButton,
            html.H6('Result:'),
            html.Div(id='check-result'),
        ],
        id='upload-result-section',
    ),
    html.Hr(),
    html.Div(id='slider-value'),
    html.Div(id='slider-output')
], className='container')


def parse_contents(contents, filename, date):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')))
        elif 'xls' in filename or 'xlsx' in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))
        else:
            raise Exception('unknown extension')
    except Exception:
        return [[], html.Div([
            'There was an error processing this file.'
        ])]

    # df2 = pd.DataFrame(df.dtypes).reset_index()
    # df2.columns = ['Column', 'Type']

    return [
        [dict(label=col, value=col) for col in df.columns],
        html.Div([
            html.H5(filename),
            html.H6(datetime.datetime.fromtimestamp(date)),
            dash_table.DataTable(
                data=df.round(4).to_dict('records'),
                columns=[{'name': i, 'id': i} for i in df.columns],
                row_selectable='multi',
                selected_rows=[],
                editable=True,
                virtualization=True,
                page_action='none'
            ),

            # (주의) 여기서 최종 결과를 만들면 callback을 걸 수가 없습니다.
            # html.Div([
            #     html.H6('x columns'),
            #     ColumnChecklist,
            # ]),
            # html.Div([
            #     html.H6('y column'),
            #     ColumnSelector,
            # ]),
            # ColumnSubmitButton,
            # dash_table.DataTable(
            #     data=df.to_dict('records'),
            #     columns=[{'name': i, 'id': i} for i in df.columns]
            # ),

            # html.Hr(),  # horizontal line

            # # For debugging, display the raw contents provided by the web browser
            # html.Div('Raw Content'),
            # html.Pre(contents[0:200] + '...', style={
            #     'whiteSpace': 'pre-wrap',
            #     'wordBreak': 'break-all'
            # })
        ]),
    ]


def train_test_set(df, features, label, ratio):
    x = df[df.columns.intersection(features)]
    y = df[df.columns.intersection(label)]
    X_train, X_test, y_train, y_test = sklearn.model_selection.train_test_split(x, y, test_size=ratio)
    return X_train, X_test, y_train, y_test


@app.callback([Output('column-checkboxes', 'options'),
               Output('column-selector', 'options'),
               Output('output-data-upload', 'children'),
               Output('upload-result-section', 'style')],
              [Input('upload-data', 'contents')],
              [State('upload-data', 'filename'),
               State('upload-data', 'last_modified')])
def update_output(content, name, date):
    if content is not None:
        options, content = parse_contents(content, name, date)
        return (
            options,
            options,
            content,
            dict(display='block')
        )
    else:
        return (list(), list(), None, dict(display='none'))


@app.callback(Output('check-result', 'children'),
              [Input('submit-button', 'n_clicks')],
              [State('column-checkboxes', 'value'), State('column-selector', 'value')])
def forward_to_next_step(*args):
    print(args)
    result = []
    if args[1]:
        result.append(html.Div(['x: ', html.Span(str(args[1]), style={'font-weight': 'bold'})]))
    if args[2]:
        result.append(html.Div(['y: ', str(args[2])]))
    return html.Div(result)


@app.callback(Output('slider', 'children'),
              Output('Slider-value', 'children')
              [Input('check-result', 'children')],
              [State('column-checkboxes', 'value'), State('column-selector', 'value')])
def slider_value(*args):
    if args[1] and args[2] is not None:
        return html.Div([html.P('Train-Test set 비율'),
                         dcc.Slider(
                             id='my-slider',
                             marks={0: 'Train Set', 0.2: '0.2', 0.4: '0.4', 0.6: '0.6', 0.8: '0.8', 1: 'Test Set'},
                             min=0,
                             max=1,
                             step=0.05,
                             value=0.75,
                             updatemode='drag'
                         )],
                        ,

# 슬라이더 밑에 텍스트 뜨게 해야함

@app.callback(Output('train-test-sets', 'children'),
              [Input('output-data-upload', 'value')],
              [State('column-checkboxes', 'value'), State('column-selector', 'value'), ])
def train_test_set_split(df, features, label, ratio):
    if slider is not None:
        return html.Div


if __name__ == '__main__':
    app.run_server(debug=True)
