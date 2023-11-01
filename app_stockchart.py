import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from streamlit_lottie import st_lottie
import plotly.express as px
import requests

# Hàm load dữ liệu từ URL sử dụng thư viện requests
def load_lottieurl(url):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

# Hàm main chạy ứng dụng Streamlit
def main():
    # Cấu hình trang Streamlit
    st.set_page_config(page_title="Stock Dashboard", page_icon="📈", layout="wide")

    # Tải dữ liệu Lottie animations từ URL
    stock1 = load_lottieurl("https://lottie.host/c9bc0a11-4290-48b5-9597-f0f0ebdf7308/fSkUtq2VN2.json")
    stock2 = load_lottieurl("https://lottie.host/cc8b8e95-e25e-4115-8b18-2f93208455f2/BtgpHgRIAN.json")

    # Tạo layout cột trái và cột phải
    left_column, right_column = st.columns(2)

    # Hiển thị animation ở cột phải
    with right_column:
        st_lottie(stock1, height=300, key="stock1")

    # Hiển thị tiêu đề và thông tin ở cột trái
    with left_column:
        st.title("📈 Stock Dashboard")
        st.subheader("🔔 Welcome to the Stock Dashboard!")
        st.write("Just upload stock data, and the site will provide insights and visualizations.")

    # Sidebar để tải dữ liệu từ tệp Excel
    with st.sidebar:
        st.sidebar.header("Data Source")
        file = st.sidebar.file_uploader("Please upload an Excel file:", type=["xls", "xlsx"])
        data_dict = load_data_from_file(file)
        st_lottie(stock2, width=250, height=250, key="stock2")

    if data_dict is not None:
        symbol_data, price_data = prepare_data(data_dict)

        options = st.sidebar.radio('Pages', options=['Data Analysis', 'Data Visualization'])
        if options == 'Data Analysis':
            data_analysis_page(symbol_data, price_data)
        elif options == 'Data Visualization':
            data_visualization_page(price_data, symbol_data)

# Đánh dấu hàm này để lưu trữ dữ liệu tải lên trong bộ nhớ cache
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

# Chuẩn bị dữ liệu cho việc hiển thị
def prepare_data(data_dict):
    symbol_data = data_dict['Symbol']
    price_data = data_dict['Price']

    # Trích xuất thông tin RIC từ cột Symbol
    symbol_data['RIC'] = symbol_data['Symbol'].str.split('VT:').str[1]
    ric = dict(zip(symbol_data['Name'], symbol_data['RIC']))

    # Đổi tên cột Date thành 'Date' và loại bỏ hàng đầu tiên
    price_data.rename(columns=ric, inplace=True)
    price_data = price_data.rename(columns={'Name': 'Date'})
    price_data.dropna(how='all', inplace=True, subset=price_data.columns[1:])
    price_data.drop(0, inplace=True)

    return symbol_data, price_data

# Trang Data Analysis
def data_analysis_page(symbol_data, price_data):
    st.header("Data Analysis")
    col1, col2 = st.columns(2)
    with col1:
        st.write("Stock Data:")
        st.write(symbol_data)
    with col2:
        st.write("Price Data:")
        st.write(price_data)
    tab1, tab2 = st.columns(2)
    with tab1:
        st.header("Sector Bar Chart")
        sector_counts = symbol_data['Sector'].value_counts()
        color_palette = px.colors.qualitative.Light24
        fig_sector = px.bar(x=sector_counts.index, y=sector_counts.values, title='Number of Stocks by Sector',
                            color_discrete_sequence=color_palette)
        st.plotly_chart(fig_sector, use_container_width=True)

    with tab2:
        st.header("Exchange Pie Chart")
        exchange_counts = symbol_data['Exchange'].value_counts()
        fig_exchange = go.Figure([go.Pie(labels=exchange_counts.index, values=exchange_counts.values)])
        fig_exchange.update_layout(title='Number of Stocks by Exchange')
        st.plotly_chart(fig_exchange, use_container_width=True)

# Trang Data Visualization
def data_visualization_page(price_data, symbol_data):
    st.header("Data Visualization")

    symbol = st.selectbox('Enter stock code (Example: VCB):', price_data.columns[1:]).upper()

    if symbol not in price_data.columns:
        st.warning("Invalid stock code. Please enter a valid stock code.")
    else:
        selected_data = select_data_to_visualize(price_data, symbol)
        visualize_stock_data(symbol, selected_data, symbol_data)

# Lựa chọn dữ liệu để hiển thị
def select_data_to_visualize(price_data, symbol):
    col1, col2 = st.columns(2)
    price_data["Date"] = pd.to_datetime(price_data["Date"])
    with col1:
        date1 = pd.to_datetime(st.date_input("Start date", price_data["Date"].min()))
    with col2:
        date2 = pd.to_datetime(st.date_input("End date", price_data["Date"].max()))
    selected_data = price_data[(price_data['Date'] >= date1) & (price_data['Date'] <= date2)]
    selected_data = selected_data[['Date', symbol]].dropna(subset=[symbol])
    return selected_data

# Hiển thị dữ liệu và biểu đồ
def visualize_stock_data(symbol, selected_data, symbol_data):
    st.markdown('### Time Series Analysis')
    left_column, right_column = st.columns((7, 3))
    with right_column:
        with st.expander("Price Data"):
            data1 = selected_data
            st.write(data1)
        with st.expander("Stock Information"):
            selected_stock_info = symbol_data[symbol_data['RIC'] == symbol]
            if not selected_stock_info.empty:
                full_name = selected_stock_info['Full Name'].values[0]
                start_date = selected_stock_info['Start Date'].values[0]
                category = selected_stock_info['Category'].values[0]
                exchange = selected_stock_info['Exchange'].values[0]
                market = selected_stock_info['Market'].values[0]
                currency = selected_stock_info['Currency'].values[0]
                sector = selected_stock_info['Sector'].values[0]

                st.write(f"Full Name: {full_name}")
                st.write(f"Start Date: {start_date}")
                st.write(f"Category: {category}")
                st.write(f"Exchange: {exchange}")
                st.write(f"Market: {market}")
                st.write(f"Currency: {currency}")
                st.write(f"Sector: {sector}")
    with left_column:
        selected_indicators = st.multiselect('Select Technical Indicators:',
                                             ['SMA', 'EMA', 'Bbands', 'MACD', 'RSI', 'Stochastic'])
        fig = make_subplots(rows=4, cols=1, shared_xaxes=True, vertical_spacing=0.02, row_heights=[0.4, 0.2, 0.2, 0.2])

        add_price_chart_to_subplot(fig, selected_data, symbol, row=1, col=1)

        for indicator in selected_indicators:
            if indicator == "SMA":
                n_sma = st.number_input("SMA Length", value=50, min_value=1)
                add_sma(fig, selected_data, symbol, n_sma)

            elif indicator == "EMA":
                n_ema = st.number_input("EMA Length", value=12, min_value=1)
                add_ema(fig, selected_data, symbol, n_ema)

            elif indicator == "Bbands":
                add_bollinger_bands(fig, selected_data, symbol, 20, 2)

            elif indicator == "MACD":
                add_macd_to_subplot(fig, selected_data, symbol, row=2, col=1)

            elif indicator == "RSI":
                add_rsi_to_subplot(fig, selected_data, symbol, row=3, col=1)

            elif indicator == "Stochastic":
                add_stochastic_to_subplot(fig, selected_data, symbol, row=4, col=1)

        fig.update_yaxes(title_text='Price', row=1, col=1)
        st.plotly_chart(fig, use_container_width=True)

# Thêm biểu đồ giá vào subplot
def add_price_chart_to_subplot(fig, data, symbol, row, col):
    fig.add_trace(go.Scatter(x=data['Date'], y=data[symbol], name='Price', line=dict(color='blue')), row=row, col=col)

# Thêm biểu đồ RSI vào subplot
def add_rsi_to_subplot(fig, data, symbol, row, col):
    n_rsi = 14
    delta = data[symbol].diff(1)
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    average_gain = gain.rolling(window=n_rsi).mean()
    average_loss = loss.rolling(window=n_rsi).mean()
    rs = average_gain / average_loss
    rsi = 100 - (100 / (1 + rs))

    fig.add_trace(go.Scatter(x=data['Date'], y=rsi, name='RSI', line=dict(color='purple')), row=row, col=col)
    fig.add_shape(type='line', x0=data['Date'].min(), x1=data['Date'].max(), y0=70, y1=70,
                  line=dict(color='red', width=2, dash='dash'), xref='x', yref='y', row=row, col=col)
    fig.add_shape(type='line', x0=data['Date'].min(), x1=data['Date'].max(), y0=30, y1=30,
                  line=dict(color='green', width=2, dash='dash'), xref='x', yref='y', row=row, col=col)

# Thêm biểu đồ MACD vào subplot
def add_macd_to_subplot(fig, data, symbol, row, col):
    f_macd = 12
    s_macd = 26
    c_macd = 9

    data[f'12_EMA'] = data[symbol].ewm(span=f_macd).mean()
    data[f'26_EMA'] = data[symbol].ewm(span=s_macd).mean()
    data[f'MACD'] = data[f'12_EMA'] - data[f'26_EMA']
    data[f'SIGNAL'] = data[f'MACD'].ewm(span=c_macd, adjust=False).mean()

    fig.add_trace(go.Scatter(x=data['Date'], y=data[f'MACD'], name='MACD', line=dict(color='blue')), row=row, col=col)
    fig.add_trace(go.Scatter(x=data['Date'], y=data[f'SIGNAL'], name='Signal Line', line=dict(color='red')), row=row, col=col)

# Thêm biểu đồ Stochastic vào subplot
def add_stochastic_to_subplot(fig, data, symbol, row, col):
    k_stoch = 14
    d_stoch = 3

    data[symbol] = pd.to_numeric(data[symbol], errors='coerce')
    stoch_k = 100 * (data[symbol] - data[symbol].rolling(window=k_stoch).min()) / (
            data[symbol].rolling(window=k_stoch).max() - data[symbol].rolling(window=k_stoch).min())
    stoch_d = stoch_k.rolling(window=d_stoch).mean()

    fig.add_trace(go.Scatter(x=data['Date'], y=stoch_k, line=dict(color='orange', width=1.5), name='Stochastic %K'), row=row, col=col)
    fig.add_trace(go.Scatter(x=data['Date'], y=stoch_d, line=dict(color='blue', width=1.5), name='Stochastic %D'), row=row, col=col)

    fig.add_shape(type='line', x0=data['Date'].min(), x1=data['Date'].max(), y0=80, y1=80,
                  line=dict(color='red', width=2, dash='dash'), xref='x', yref='y', row=row, col=col)
    fig.add_shape(type='line', x0=data['Date'].min(), x1=data['Date'].max(), y0=20, y1=20,
                  line=dict(color='green', width=2, dash='dash'), xref='x', yref='y', row=row, col=col)

# Thêm biểu đồ SMA vào subplot
def add_sma(fig, data, symbol, n):
    data[f'SMA{n}'] = data[symbol].rolling(window=n).mean()
    fig.add_trace(go.Scatter(x=data['Date'], y=data[f'SMA{n}'], name=f'SMA{n} {symbol}', line=dict(color='red')))

# Thêm biểu đồ EMA vào subplot
def add_ema(fig, data, symbol, n):
    data[f'EMA{n}'] = data[symbol].ewm(span=n, adjust=False).mean()
    fig.add_trace(go.Scatter(x=data['Date'], y=data[f'EMA{n}'], name=f'EMA{n} {symbol}', line=dict(color='green')))

# Thêm biểu đồ Bollinger Bands vào subplot
def add_bollinger_bands(fig, data, symbol, n, k):
    data[f'SMA{n}'] = data[symbol].rolling(window=n).mean()
    data[f'Upper{n}'] = data[f'SMA{n}'] + (k * data[symbol].rolling(window=n).std())
    data[f'Lower{n}'] = data[f'SMA{n}'] - (k * data[symbol].rolling(window=n).std())
    fig.add_trace(go.Scatter(x=data['Date'], y=data[f'Upper{n}'], name=f'Upper Bollinger Band', line=dict(color='red')))
    fig.add_trace(go.Scatter(x=data['Date'], y=data[f'Lower{n}'], name=f'Lower Bollinger Band', line=dict(color='green')))

if __name__ == "__main__":
    main()
