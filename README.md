Project Description

This project utilizes the Spring framework as the main server node, with Python microservices that are managed and executed through Spring. These microservices provide real-time price data of selected stock symbols via HTTP communication through brokers' APIs (default support for MT5 and FP Markets). The collected price data is then processed into consistent time intervals, making it suitable for advanced technical analysis.

The software allows for the creation of complex mathematical models across multiple symbols simultaneously, enabling the testing of various analytical ideas and strategies that exceed the capabilities of typical trading platforms. By leveraging a lightweight in-memory database (currently H2 embedded in the Spring environment), the application provides high efficiency in handling data, with no need to store historical results permanently. Instead, users can retrieve any number of historical entries for a given symbol on saved stock companies stored in the database. This ensures a structured and dynamic selection of symbols tailored to the broker's API requirements and user preferences.

The data retrieval rate is configurable to ensure it does not exceed the provider’s limits, with a current agreed-upon rate of 50–80 queries per second. For now, options are managed through HTTP requests via Postman,
but a simple graphical interface is planned for future development to enhance user interaction.
This project aims to offer a flexible, high-performance interface for stock data processing, allowing for powerful mathematical and technical analysis capabilities that go beyond common trading tools like cTrader, MT5, or TradingView.
