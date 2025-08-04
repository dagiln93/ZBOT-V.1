# Z-Score Trading Bot

## Overview

A Flask-based web application that implements a Z-Score mean reversion trading strategy for cryptocurrency perpetual futures. The system analyzes historical price data from Bybit exchange to identify potential trading opportunities using statistical indicators. The application provides a simple web interface for executing analysis and viewing trading signals with risk management parameters.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Flask Web Framework**: Simple server-side rendered application using Jinja2 templates
- **Cyberpunk Design System**: Futuristic interface with neon colors, glitch effects, and holographic styling
- **Multi-Language Support**: Russian/English language switching with session-based persistence
- **Interactive Effects**: Matrix background, scanner lines, pulsing elements, and hologram sweeps
- **Custom Typography**: Orbitron and Roboto Mono fonts for cyberpunk aesthetic
- **Single Page Application**: Main interface on index route with form-based interaction

### Backend Architecture
- **Flask Application**: Lightweight web server handling GET/POST requests
- **Modular Design**: Core trading logic separated into `zcore.py` module
- **Error Handling**: Comprehensive exception handling with user feedback via Flask flash messages
- **Configuration Management**: Environment variable-based configuration for API credentials

### Trading Strategy Implementation
- **Z-Score Calculation**: Statistical mean reversion strategy using 14-period moving averages
- **Risk Management**: Built-in stop-loss (0.5%) and take-profit (1.0%) parameters
- **Multi-Timeframe Analysis**: 4-hour candlestick data with 30-day historical lookback
- **Signal Generation**: Threshold-based entry signals (±2.0 standard deviations)

### Data Processing
- **Pandas Integration**: DataFrame-based data manipulation and technical analysis
- **NumPy Support**: Mathematical operations for statistical calculations
- **Real-time Data**: Live market data processing from exchange API

## External Dependencies

### Cryptocurrency Exchange API
- **Bybit API**: Primary data source via `pybit` library for perpetual futures data
- **Public/Private Access**: Supports both authenticated and public API access
- **Rate Limiting**: Handles API response codes and error conditions

### Python Libraries
- **Flask**: Web framework for HTTP request handling and template rendering
- **pandas**: Data manipulation and analysis for price data processing
- **numpy**: Numerical computing for statistical calculations
- **pybit**: Official Bybit API client for market data retrieval

### Frontend Dependencies
- **Bootstrap**: UI framework via CDN for responsive design
- **Font Awesome**: Icon library for visual elements
- **Replit Bootstrap Theme**: Dark theme variant optimized for the platform

### Environment Configuration
- **Session Management**: Flask secret key configuration via environment variables
- **API Credentials**: Optional Bybit API key/secret for authenticated requests
- **Development Settings**: Debug mode and host configuration for deployment