

# shopDEV-python

Welcome to the shopDEV-python repository. This is a backend service for an e-commerce platform, designed with best practices in mind to provide a robust and scalable service.

## Getting Started

These instructions will get your copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

Before you begin, ensure you have the following installed:
- Python 3.8+
- pip (Python package installer)
- MongoDB

### Installing

A step-by-step series of examples that tell you how to get a development environment running.

1. **Install requirements.txt**

Navigate to the project directory and run:

```bash
pip install -r requirements.txt
```

This command will install all the necessary Python packages listed in `requirements.txt`.

2. **Setup MongoDB on Linux**

Ensure that MongoDB is installed and running on your system. If not, follow the official MongoDB documentation to set it up: [MongoDB Installation Guide](https://docs.mongodb.com/manual/installation/).

3. **Environment Variables**

Create a `.env` file in the root directory of the project and add the following line:

```env
MONGO_CONNECTION_STRING=mongodb://localhost:27017/shopDEV
```

Adjust the connection string if you have a different configuration.

4. **Run the Application**

To start the server, navigate to the project directory and run:

```bash
python3 server.py
```

The server should start, and you'll be able to access the API at `http://localhost:3055`.

## Remove all pycache

find ./ -type d -name "__pycache__" -exec rm -r {} \;

## Running the Tests

Explain how to run the automated tests for this system (if available).

## Deployment

Add additional notes about how to deploy this on a live system.

## Built With

* [FastAPI](https://fastapi.tiangolo.com/) - The web framework used
* [Motor](https://motor.readthedocs.io/en/stable/) - The asynchronous MongoDB driver for Python
* [Pydantic](https://pydantic-docs.helpmanual.io/) - Data validation and settings management using Python type annotations

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct, and the process for submitting pull requests to us.

## Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/yourusername/shopDEV-python/tags).

## Authors

* **Le Thanh Son** - *Initial work* - [lethanhson9901](https://github.com/lethanhson9901)

See also the list of [contributors](https://github.com/yourusername/shopDEV-python/contributors) who participated in this project.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* Hat tip to anyone whose code was used
* Inspiration
* etc
```

