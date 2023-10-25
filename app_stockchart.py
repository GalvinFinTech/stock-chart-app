#pip install streamlit
#pip install pandas
#pip install plotly
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Dashboard", page_icon="🌍", layout="wide")
st.title(" :bar_chart: Dashboard")
st.subheader("🔔 Analytics")
st.markdown('<style>div.block-container{padding-top:1rem;}</style>', unsafe_allow_html=True)

@st.cache_data
def load_data_from_file(file):
    if file is not None:
        file_extension = file.name.split(".")[-1]
        if file_extension in ["xls", "xlsx"]:
            xls = pd.ExcelFile(file)
            data_dict = {sheet_name: xls.parse(sheet_name) for sheet_name in xls.sheet_names}
            return data_dict
        else:
            st.warning("Unsupported file format. Please upload an Excel file.")
    else:
        st.warning("No data loaded.")
    return None
def main():
    # Sidebar cho việc tải dữ liệu
    st.sidebar.header("Data Source")
    file = st.sidebar.file_uploader("Please upload an Excel file:", type=["xls", "xlsx"])
    data_dict = load_data_from_file(file)
    if data_dict is not None:
        symbol_data = data_dict['Symbol']
        price_data = data_dict['Price']

        symbol_data['RIC'] = symbol_data['Symbol'].str.split('VT:').str[1]
        ric = dict(zip(symbol_data['Name'], symbol_data['RIC']))
        price_data.rename(columns=ric, inplace=True)
        price_data = price_data.rename(columns={'Name': 'Date'})

        price_data.dropna(how='all', inplace=True, subset=price_data.columns[1:])
        price_data.drop(0, inplace=True)

        options = st.sidebar.radio('Pages', options=['Data Analysis', 'Data Visualization'])

        if options == 'Data Analysis':
            st.header("Data Analysis")
            st.write("Stock Data:")
            st.write(symbol_data)
            st.write("Price Data:")
            st.write(price_data)
            tab1, tab2 = st.tabs(["Sector", "Exchange"])
            with tab1:
                st.header("Sector Bar Chart")
                sector_counts = symbol_data['Sector'].value_counts()
                fig_sector = go.Figure([go.Bar(x=sector_counts.index, y=sector_counts.values)])
                fig_sector.update_layout(title='Số lượng cổ phiếu theo ngành')
                st.plotly_chart(fig_sector)

            # Tab 2: Biểu đồ tròn cho số lượng cổ phiếu theo sàn giao dịch
            with tab2:
                st.header("Exchange Pie Chart")
                exchange_counts = symbol_data['Exchange'].value_counts()
                fig_exchange = go.Figure([go.Pie(labels=exchange_counts.index, values=exchange_counts.values)])
                fig_exchange.update_layout(title='Số lượng cổ phiếu theo sàn giao dịch')
                st.plotly_chart(fig_exchange)

        elif options == 'Data Visualization':
            st.header("Data Visualization")
            st.sidebar.header("Choose your filter:")

            symbol = st.sidebar.text_input('Enter stock code (Example: VCB):', value=price_data.columns[1])

            if symbol not in price_data.columns:
                st.warning("Invalid stock code. Please enter a valid stock code.")
            else:
                chart_type = st.sidebar.selectbox('Select Chart Type', ['Line', 'Bar', 'Scatter', 'Histogram'])
                selected_indicators = st.sidebar.multiselect('Choose technical indicators',
                                                             ['MACD', 'RSI', 'SMA', 'BBands', 'EMA',
                                                              'Stochastic Oscillator'])

            col1, col2 = st.columns((2))
            price_data["Date"] = pd.to_datetime(price_data["Date"])
            start_date = price_data["Date"].min()
            end_date = price_data["Date"].max()
            with col1:
                date1 = pd.to_datetime(st.date_input("Start date", start_date))
            with col2:
                date2 = pd.to_datetime(st.date_input("End date", end_date))

            st.markdown('### Time Series Analysis')
            selected_data = price_data[(price_data['Date'] >= date1) & (price_data['Date'] <= date2)]
            selected_data = selected_data[['Date', symbol]].dropna(subset=[symbol])
            left_column, right_column = st.columns((7, 3))
            with right_column:
                with st.expander("Price Data"):
                    data1 = selected_data
                    st.write(data1)
            with left_column:
                if chart_type == 'Line':
                    # Tạo biểu đồ đường
                    fig = go.Figure()
                    fig.add_trace(
                        go.Scatter(x=selected_data['Date'], y=selected_data[symbol], mode='lines', name=symbol,
                                   line=dict(color='blue')))
                    fig.update_xaxes(title_text='Ngày', rangeslider_visible=True, rangeselector=dict(
                        buttons=[
                            dict(count=1, label="1m", step="month", stepmode="backward"),
                            dict(count=6, label="6m", step="month", stepmode="backward"),
                            dict(count=1, label="YTD", step="year", stepmode="todate"),
                            dict(count=1, label="1y", step="year", stepmode="backward"),
                            dict(step="all")
                        ]
                    ))
                    fig.update_yaxes(title_text='Giá đóng cửa')
                    fig.update_layout(title=f'Biểu đồ đường của mã cổ phiếu {symbol}')
                elif chart_type == 'Bar':
                    # Tạo biểu đồ cột
                    fig = go.Figure()
                    fig.add_trace(
                        go.Bar(x=selected_data['Date'], y=selected_data[symbol], name=symbol, marker_color='blue'))
                    fig.update_xaxes(title_text='Ngày', rangeslider_visible=True, rangeselector=dict(
                        buttons=[
                            dict(count=1, label="1m", step="month", stepmode="backward"),
                            dict(count=6, label="6m", step="month", stepmode="backward"),
                            dict(count=1, label="YTD", step="year", stepmode="todate"),
                            dict(count=1, label="1y", step="year", stepmode="backward"),
                            dict(step="all")
                        ]
                    ))
                    fig.update_yaxes(title_text='Giá đóng cửa')
                    fig.update_layout(title=f'Biểu đồ cột của mã cổ phiếu {symbol}')

                elif chart_type == 'Scatter':
                    fig = go.Figure()
                    fig.add_trace(
                        go.Scatter(x=selected_data['Date'], y=selected_data[symbol], mode='markers', name=symbol,
                                   marker=dict(color='blue')))
                    fig.update_xaxes(title_text='Ngày', rangeslider_visible=True, rangeselector=dict(
                        buttons=[
                            dict(count=1, label="1m", step="month", stepmode="backward"),
                            dict(count=6, label="6m", step="month", stepmode="backward"),
                            dict(count=1, label="YTD", step="year", stepmode="todate"),
                            dict(count=1, label="1y", step="year", stepmode="backward"),
                            dict(step="all")
                        ]
                    ))
                    fig.update_yaxes(title_text='Giá đóng cửa')
                    fig.update_layout(title=f'Biểu đồ phân tán của mã cổ phiếu {symbol}')

                elif chart_type == 'Histogram':
                    # Tạo biểu đồ histogram
                    fig = go.Figure()
                    fig.add_trace(go.Histogram(x=selected_data[symbol], name=symbol, marker_color='blue'))
                    fig.update_xaxes(title_text='Giá đóng cửa')
                    fig.update_yaxes(title_text='Số lần')
                    fig.update_layout(title=f'Biểu đồ histogram của mã cổ phiếu {symbol}')
                st.plotly_chart(fig)

                with st.expander("Thông tin về mã cổ phiếu"):
                        selected_stock_info = symbol_data[symbol_data['RIC'] == symbol]  # Lọc thông tin cho mã cổ phiếu đã chọn
                        if not selected_stock_info.empty:
                            full_name = selected_stock_info['Full Name'].values[0]
                            start_date = selected_stock_info['Start Date'].values[0]
                            category = selected_stock_info['Category'].values[0]
                            exchange = selected_stock_info['Exchange'].values[0]
                            market = selected_stock_info['Market'].values[0]
                            currency = selected_stock_info['Currency'].values[0]
                            sector = selected_stock_info['Sector'].values[0]

                            st.write(f"Tên đầy đủ: {full_name}")
                            st.write(f"Ngày bắt đầu: {start_date}")
                            st.write(f"Loại: {category}")
                            st.write(f"Sàn giao dịch: {exchange}")
                            st.write(f"Thị trường: {market}")
                            st.write(f"Tiền tệ: {currency}")
                            st.write(f"Ngành: {sector}")
            with st.expander("Technical Indicator"):
                for indicator in selected_indicators:
                    if indicator == "MACD":
                        f = st.number_input("FastLength", value=12, min_value=1)
                        s = st.number_input("SlowLength", value=26, min_value=1)
                        c = st.number_input("SignalLength", value=9, min_value=1)
                        selected_data['12_EMA'] = selected_data[symbol].ewm(span=f).mean()
                        selected_data['26_EMA'] = selected_data[symbol].ewm(span=s).mean()
                        selected_data['MACD'] = selected_data['12_EMA'] - selected_data['26_EMA']
                        selected_data['SIGNAL'] = selected_data['MACD'].ewm(span=c, adjust=False).mean()
                        selected_data['MACD_HIST'] = selected_data['MACD'] - selected_data['12_EMA']

                        fig = go.Figure()
                        fig.add_trace(go.Scatter(x=selected_data['Date'], y=selected_data['MACD'], name='MACD',
                                                 line=dict(color='orange')))
                        fig.add_trace(go.Scatter(x=selected_data['Date'], y=selected_data['SIGNAL'], name='Signal Line',
                                                 line=dict(color='blue')))
                        fig.update_xaxes(title='Date', rangeslider_visible=True)
                        fig.update_yaxes(title='Price')
                        fig.update_layout(showlegend=True)

                    elif indicator == "RSI":
                        n = st.number_input("Length", value=14, min_value=1)
                        def calculate_rsi(data, period=n):
                            delta = data.diff(1)
                            gain = delta.where(delta > 0, 0)
                            loss = -delta.where(delta < 0, 0)
                            average_gain = gain.rolling(window=period).mean()
                            average_loss = loss.rolling(window=period).mean()
                            rs = average_gain / average_loss
                            rsi = 100 - (100 / (1 + rs))
                            return rsi
                        selected_data['RSI'] = calculate_rsi(selected_data[symbol],n)

                        fig = go.Figure()
                        fig.add_trace(go.Scatter(x=selected_data['Date'], y=selected_data['RSI'], name='RSI',
                                                 line=dict(color='purple')))
                        fig.add_shape(type='line', x0=selected_data['Date'].min(), x1=selected_data['Date'].max(), y0=80, y1=80,
                                      line=dict(color='red', width=2, dash='dash'), xref='x', yref='y')
                        fig.add_shape(type='line', x0=selected_data['Date'].min(), x1=selected_data['Date'].max(), y0=20, y1=20,
                                      line=dict(color='green', width=2, dash='dash'), xref='x', yref='y')

                        fig.add_annotation(
                            x=selected_data['Date'].max(), y=80,
                            text="Overbought", showarrow=True,
                            font=dict(family="Arial", size=14, color="red"),
                            align="center", arrowhead=2, arrowsize=1, arrowwidth=2, arrowcolor="red")
                        fig.add_annotation(
                            x=selected_data['Date'].max(), y=20,
                            text="Oversold", showarrow=True,
                            font=dict(family="Arial", size=14, color="green"),
                            align="center", arrowhead=2, arrowsize=1, arrowwidth=2, arrowcolor="green")

                        fig.update_xaxes(title='Date', rangeslider_visible=True)
                        fig.update_yaxes(title='Price')
                        fig.update_layout(showlegend=True)
                    elif indicator == "SMA":
                        n = st.number_input("Length", value=50, min_value=1)
                        selected_data['SMA'] = selected_data[symbol].rolling(window=n).mean()
                        fig = go.Figure()
                        fig.add_trace(go.Scatter(x=selected_data['Date'], y=selected_data[symbol], name='Giá cổ phiếu',
                                                 line=dict(color='blue')))
                        fig.add_trace(go.Scatter(x=selected_data['Date'], y=selected_data['SMA'], name=f'SMA {n} ngày',
                                                 line=dict(color='red')))
                        fig.update_xaxes(title='Date', rangeslider_visible=True)
                        fig.update_yaxes(title='Price')
                        fig.update_layout(showlegend=True)

                    elif indicator == "BBands":
                        n = st.number_input("Length", value=20, min_value=1)
                        k = st.number_input("Mult", value=2, min_value=1)
                        selected_data['SMA'] = selected_data[symbol].rolling(window=n).mean()
                        selected_data['Upper'] = selected_data['SMA'] + (k * selected_data[symbol].rolling(window=n).std())
                        selected_data['Lower'] = selected_data['SMA'] - (k * selected_data[symbol].rolling(window=n).std())

                        fig = go.Figure()
                        fig.add_trace(go.Scatter(x=selected_data['Date'], y=selected_data[symbol], name='Stock Price',
                                             line=dict(color='blue')))
                        fig.add_trace(go.Scatter(x=selected_data['Date'], y=selected_data['SMA'], name=f'SMA {n} Days',
                                             line=dict(color='red')))
                        fig.add_trace(
                        go.Scatter(x=selected_data['Date'], y=selected_data['Upper'], name='Upper Bollinger Band',
                                   line=dict(color='green')))
                        fig.add_trace(
                        go.Scatter(x=selected_data['Date'], y=selected_data['Lower'], name='Lower Bollinger Band',
                                   line=dict(color='purple')))
                        fig.update_xaxes(title='Date', rangeslider_visible=True)
                        fig.update_yaxes(title='Price')
                        fig.update_layout(showlegend=True)


                    elif indicator == "EMA":
                        n = st.number_input("Length", value=12, min_value=1)
                        selected_data['EMA'] = selected_data[symbol].ewm(span=n, adjust=False).mean()
                        fig = go.Figure()
                        fig.add_trace(go.Scatter(x=selected_data['Date'], y=selected_data[symbol], name='Giá cổ phiếu',
                                                 line=dict(color='blue')))
                        fig.add_trace(go.Scatter(x=selected_data['Date'], y=selected_data['EMA'], name=f'EMA {n} ngày',
                                                 line=dict(color='red')))

                        fig.update_xaxes(title='Date', rangeslider_visible=True)
                        fig.update_yaxes(title='Price')
                        fig.update_layout(showlegend=True)
                    elif indicator == 'Stochastic Oscillator':
                        k_period = st.number_input("K Period", value=14, min_value=1)
                        d_period = st.number_input("D Period", value=3, min_value=1)
                        selected_data[symbol] = pd.to_numeric(selected_data[symbol], errors='coerce')
                        stoch_k = 100 * (selected_data[symbol] - selected_data[symbol].rolling(window=k_period).min()) / (
                                selected_data[symbol].rolling(window=k_period).max() - selected_data[symbol].rolling(
                            window=k_period).min())
                        stoch_d = stoch_k.rolling(window=d_period).mean()

                        fig = go.Figure()
                        fig.add_trace(go.Scatter(x=stoch_k.index, y=stoch_k, mode='lines', name='Stochastic K'))
                        fig.add_trace(go.Scatter(x=stoch_d.index, y=stoch_d, mode='lines', name='Stochastic D'))
                    st.markdown(f'### {indicator}')
                    st.plotly_chart(fig, use_container_width=True)
if __name__ == "__main__":
    main()


