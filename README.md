# Backend API for Connect The Memories
| Routes                                                                                                                                                             | Type | Inputs                      |
|--------------------------------------------------------------------------------------------------------------------------------------------------------------------|------|-----------------------------|
| [/api/auth/create_account](https://github.com/Connect-The-Memories/connect-the-memories-backend/blob/c7c89716943adb24c80af25f084e998add14755e/auth/routes.py#L38)  | POST | Email, Password, ETC        | 
| [/api/auth/delete_account](https://github.com/Connect-The-Memories/connect-the-memories-backend/blob/c7c89716943adb24c80af25f084e998add14755e/auth/routes.py#L126) | POST | Token ID from Active User   |
| [/api/auth/logging_in](https://github.com/Connect-The-Memories/connect-the-memories-backend/blob/c7c89716943adb24c80af25f084e998add14755e/auth/routes.py#L77)      | POST | Email, Password             |
| [/api/auth/logout](https://github.com/Connect-The-Memories/connect-the-memories-backend/blob/c7c89716943adb24c80af25f084e998add14755e/auth/routes.py#L97)          | POST | None                        | 
| [/api/auth/reset_password](https://github.com/Connect-The-Memories/connect-the-memories-backend/blob/c7c89716943adb24c80af25f084e998add14755e/auth/routes.py#L107) | POST | Email                       |
