<div align="center">

[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]
[![LinkedIn][linkedin-shield]][linkedin-url]

</div>

<a name="readme-top"></a>

<h3 align="center">Tradingview To EXCH API</h3>

<p align="center">
  Professional bridge REST API between TradingView webhooks and Binance Exchange.
<br /><br />
<a href="https://github.com/GstMirabal/Tradingview2EXCH"><strong>Explore the docs »</strong></a>
<br />
·
<a href="https://github.com/GstMirabal/Tradingview2EXCH/issues/new?labels=bug&template=bug-report---.md">Report Bug</a>
·
<a href="https://github.com/GstMirabal/Tradingview2EXCH/issues/new?labels=enhancement&template=feature-request---.md">Request Feature</a>
</p>

<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul><li><a href="#built-with">Built With</a></li></ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation & Configuration</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
  </ol>
</details>

## About The Project

This project provides a robust, production-ready solution to automate trading strategies by receiving TradingView alerts and executing corresponding orders on Binance. Built with a modular Django architecture, it features enhanced security (HSTS, CSP, Passphrase validation), real-time logging, and professional configuration management via TOML and environment variables.

### Key Features:
- **Modular Structure**: Discovered and isolated apps for webhooks and exchange interaction.
- **Service Layer Architecture**: Decoupled business logic for clean maintenance and testing.
- **Enhanced Security**: Passphrase-protected endpoints and strict environment separation.
- **Industrial Logging**: Configurable JSON/Text logs with rotation.
- **Auto-Doc**: Integrated Swagger/Redoc UI for API management.

### Built With

[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white)](https://www.djangoproject.com/)
[![Binance](https://img.shields.io/badge/Binance-F3BA2F?style=for-the-badge&logo=binance&logoColor=black)](https://www.binance.com/)
[![TOML](https://img.shields.io/badge/TOML-9C4121?style=for-the-badge&logo=toml&logoColor=white)](https://toml.io/)

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Getting Started

### Prerequisites

- Python 3.12+
- Pip & venv
- Binance API Keys (with Trading permissions enabled)

### Installation & Configuration

1. **Clone the repository**
   ```bash
   git clone https://github.com/GstMirabal/Tradingview2EXCH.git
   cd Tradingview2EXCH
   ```

2. **Configure Environment Variables**
   - Copy `.env.example` to `.env`.
   - Fill in:
     - `DJANGO_SECRET_KEY`: Use a strong random key.
     - `WEBHOOK_PASSPHRASE`: A secret string to validate incoming webhooks.
     - `API_KEY` & `API_SECRET`: Your Binance credentials.

3. **Install Dependencies**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

4. **Initialize & Run**
   ```bash
   python backend/manage.py migrate
   python backend/manage.py runserver
   ```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Usage

The API provides two main endpoints for automation:

### 1. Webhook Receiver
- **Endpoint**: `POST /webhook-receiver/webhook/`
- **Security**: Requires a `passphrase` field in the JSON body matching your `.env` configuration.
- **Example Payload**:
  ```json
  {
    "passphrase": "your_secret_passphrase",
    "symbol": "{{ticker}}",
    "side": "BUY",
    "type": "MARKET",
    "size": "0.001",
    "exchange": "BINANCE"
  }
  ```

#### How to Configure in TradingView:
1.  **Alert Message**: Use the following structure in your TradingView alert's "Message" field:
    ```json
    {
      "passphrase": "your_configured_passphrase_here",
      "symbol": "{{ticker}}",
      "side": "BUY",
      "type": "MARKET",
      "size": "0.001",
      "exchange": "BINANCE",
      "time": "{{time}}",
      "interval": "{{interval}}",
      "price": "{{close}}",
      "orderId": "TV_ALERT_1"
    }
    ```
2.  **Webhook URL**: Set your alert's Webhook URL to `http://your-server-ip:8000/webhook-receiver/webhook/`.
3.  **Variable Placeholder**: Notice the use of TradingView placeholders like `{{ticker}}`, `{{time}}`, and `{{close}}` to automate the data capture.

### 2. Binance Connector (Internal/Direct)
- **Endpoint**: `POST /binance-connector/binanceParams/`
- **Purpose**: Direct order submission for internal tools.

### 3. API Documentation
Access the interactive documentation at:
- Swagger: `http://localhost:8000/swagger/`
- Redoc: `http://localhost:8000/redoc/`

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'feat: Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## License

Distributed under the MIT License. See `LICENSE.txt` for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Contact

Gustavo Mirabal Suarez - gst.mirabal@gmail.com

- LinkedIn: [@Gustavo-Mirabal](https://www.linkedin.com/in/gstmirabal/)
- GitHub: [@GstMirabal](https://github.com/GstMirabal)
- Twitter: [@GstMirabal](https://x.com/gst_mirabal)

Project Link: [https://github.com/GstMirabal/Tradingview2EXCH](https://github.com/GstMirabal/Tradingview2EXCH)

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- MARKDOWN LINKS & IMAGES -->
[contributors-shield]: https://img.shields.io/github/contributors/GstMirabal/Tradingview2EXCH.svg?style=for-the-badge
[contributors-url]: https://github.com/GstMirabal/Tradingview2EXCH/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/GstMirabal/Tradingview2EXCH.svg?style=for-the-badge
[forks-url]: https://github.com/GstMirabal/Tradingview2EXCH/network/members
[stars-shield]: https://img.shields.io/github/stars/GstMirabal/Tradingview2EXCH.svg?style=for-the-badge
[stars-url]: https://github.com/GstMirabal/Tradingview2EXCH/stargazers
[issues-shield]: https://img.shields.io/github/issues/GstMirabal/Tradingview2EXCH.svg?style=for-the-badge
[issues-url]: https://github.com/GstMirabal/Tradingview2EXCH/issues
[license-shield]: https://img.shields.io/github/license/GstMirabal/Tradingview2EXCH.svg?style=for-the-badge
[license-url]: https://github.com/GstMirabal/Tradingview2EXCH/blob/master/LICENSE.txt
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555
[linkedin-url]: https://www.linkedin.com/in/gstmirabal/
