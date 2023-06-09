===
Yaml script runner
===

This is a simple script runner that uses yaml files as a simple scripting language.

Example script:

    ---
    - set:
        - var: x
        - value: 5
    - set:
        - var: var
        - value: '"hello world"'
    - set:
        - var: var2
        - expr: var * x
    - while:
        condition: var > 0
        commands:
            - log: 
                message: "var is {{ var }}"
    # Sample comment line
            - if:
                condition: var == 5
                commands:
                    - log: 
                        msg: "condition met"
                    - set:
                        var: var
                        expr: var - 1
                    - continue
            - log:
                level: WARNING
                message: "var is {{ var }}"
            - set:
                var: url
                value: '"https://httpbin.org/get"'  # must be an expression, that's why the double quotes
            - request:
                method: GET
                url: "{{ url }}"
                headers:
                    User-Agent: "yrunner"
                params:
                    var: "{{ var }}"
                response_var: response
            - log:
                message: "response is {{ var + 1 }}  {{ response }}"
    - sleep: 5
    - exit: 0

Executable with:

    from yrunner import YRunner
    from yrunner.executors import http

    runner = YRunner(http.COMMANDS)
    result_code = runner.run(REQUEST_YAML)
    assert resut_code == 0
