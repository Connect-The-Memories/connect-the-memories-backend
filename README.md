# Backend API for Connect The Memories

- [Routes](#routes)
- [Getting Started](#getting-started)
- [Usage](#usage)

## Routes

| Routes                                                                                                                                                             | Type | Inputs                      |
|--------------------------------------------------------------------------------------------------------------------------------------------------------------------|------|-----------------------------|
| [/api/auth/create_account](https://github.com/Connect-The-Memories/connect-the-memories-backend/blob/c7c89716943adb24c80af25f084e998add14755e/auth/routes.py#L38)  | POST | Email, Password, ETC        | 
| [/api/auth/delete_account](https://github.com/Connect-The-Memories/connect-the-memories-backend/blob/c7c89716943adb24c80af25f084e998add14755e/auth/routes.py#L126) | POST | Token ID from Active User   |
| [/api/auth/logging_in](https://github.com/Connect-The-Memories/connect-the-memories-backend/blob/c7c89716943adb24c80af25f084e998add14755e/auth/routes.py#L77)      | POST | Email, Password             |
| [/api/auth/logout](https://github.com/Connect-The-Memories/connect-the-memories-backend/blob/c7c89716943adb24c80af25f084e998add14755e/auth/routes.py#L97)          | POST | None                        |  
| [/api/auth/reset_password](https://github.com/Connect-The-Memories/connect-the-memories-backend/blob/c7c89716943adb24c80af25f084e998add14755e/auth/routes.py#L107) | POST | Email                       |

## Getting Started

Here are the requirments and instructions to get this backend to run locally.

### Prerequisites

- Python 3<
- Pipenv

    ```bash
    pip install pipenv
    ```

- ```.env``` and ```serviceAccount.json``` from @Dossr-NK
- Prior to installation, make sure ```.env``` and ```serviceAccount.json``` are in the correct folders as followed:

![file_structure](/images/file_structure.png)

### Installation

1. Clone the repo

  ```bash
  git clone https://github.com/Connect-The-Memories/connect-the-memories-backend.git
  ```

2. Install packages using pipenv

  ```bash
  pipenv install
  ```

3. Access the pipenv shell

  ```bash
  pipenv shell
  ```

### Usage

Once you ahve completed installing the repo and running the installation commands. All that is left is to run flask (make sure to run it in the pipenv shell):

```bash
flask run
```