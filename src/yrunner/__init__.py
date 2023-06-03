# Basic YAML script interpreter
# Valid commands:
#  - set: set a variable
#  - request: make an HTTP request (parameters are the same as the requests library)
#  - sleep: sleep for a number of seconds (float)
#  - if: conditional execution, based on the value of a variable (>, <, ==, !=, >=, <=)
#  - while: loop execution, equal to if, but loops until the condition is false
#  - break, continue: break or continue a loop
#  - log: log a message to log (level, msg, *args, **kwargs)
#  - exit: exit the script

# Sample script:
# ---
# - set:
#     - var: x
#     - value: 5
# - set:
#     - var: var
#     - value: "hello world"
# - set:
#     - var: var2
#     - expr: var * x
# - while:
#     condition: var > 0
#     commands:
#         - log: 
#             msg: "var is {{ var }}"
#
#         - if:
#             condition: var == 5
#             commands:
#                 - log: 
#                     msg: "condition met"
#                 - set:
#                     var: var
#                     expr: var - 1
#                 - continue
#         - log:
#             message: "var is {{ var }}"
#         - request:
#             method: GET
#             url: "https://httpbin.org/get"
#             headers:
#                 User-Agent: "yrunner"
#             params:
#                 var: "{{ var }}"
#             response_var: response
#         - log: "response is {{ var }}"
# - sleep: 5
# - exit: 0
