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
#     - value: '"hello world"'
# - set:
#     - var: var2
#     - expr: var * x
# - while:
#     condition: var > 0
#     commands:
#         - log: 
#             message: "var is {{ var }}"
## Sample comments line
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
#             level: WARNING
#             message: "var is {{ var }}"
#         - set:
#             var: url
#             value: '"https://httpbin.org/get"'  # must be an expression, that's why the double quotes
#         - request:
#             method: GET
#             url: "{{ url }}"
#             headers:
#                 User-Agent: "yrunner"
#             params:
#                 var: "{{ var }}"
#             response_var: response
#         - log:
#             message: "response is {{ var + 1 }}  {{ response }}"
# - sleep: 5
# - exit: 0
