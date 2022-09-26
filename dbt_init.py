import os, re


def write_profiles(project_name: str, target:str, target_env: str, target_parameters: dict):
    os.system('cp profiles_template.yml profiles.yml')
    env_details = [
        f'{project_name}:\r\n',
        ' '*2 + f'target: {target_env}\r\n',
        ' '*2 + f'outputs:\r\n',
        ' '*4 + f'{target_env}:\r\n',
        ' '*6 + f'type: {target}\r\n'
    ]
    for parameter in target_parameters:
        if len(target_parameters[parameter]) < 1:
            target_parameters[parameter] = input(f'{parameter}:\r\n')
        env_details.append(' '*6 + f'{parameter}: {target_parameters[parameter]}\r\n')
    with open('profiles.yml', 'a') as dbt_profiles:
        dbt_profiles.writelines(env_details)
    return target_parameters


def write_project_config(project_name: str):
    os.system('cp dbt_project_template.yml dbt_project.yml')
    project_config = ''
    with open('dbt_project.yml', 'r') as project_file:
        project_config += project_file.read().replace('PROJECT_NAME', project_name)
    with open('dbt_project.yml', 'w') as project_file:
        project_file.write(project_config)


project_name = ''
schema_name =''
print('checking for existing profiles.yml...')
if os.path.exists(os.curdir + os.sep + 'profiles_backup.yml') and str(input('Copy profiles_backup instead of starting over? y/n  : ')).lower()[0] == 'y':
    with open('profiles_backup.yml', 'r') as backup_file:
        for result in re.findall(r'WAREHOUSE CONFIGURATION([#\-\s]+)([a-zA-Z_\-]+)', backup_file.read()):
            project_name = result[1]
    os.system('mkdir -p ~/.dbt && cp profiles_backup.yml ~/.dbt/profiles.yml')
else:
    project_name = str(input('What is the name of the project? Only lowercase and underscores allowed!\r\n')).lower()
    target = 'sqlserver'
    target_parameters = {
        'driver': 'ODBC Driver 18 for SQL Server',
        'server': '',
        'port': '',
        'trust_cert': 'true',
        'user': '',
        'password': '',
        'database': '',
        'schema': ''
    }
    target_env = 'dev'
    target_parameters = write_profiles(
        project_name = project_name,
        target = target,
        target_env = target_env,
        target_parameters=target_parameters
    )
    os.system('cp profiles.yml profiles_backup.yml')
    os.system('mkdir -p ~/.dbt && mv ./profiles.yml ~/.dbt/profiles.yml')

write_project_config(project_name = project_name)

os.system('dbt deps')
os.system('mkdir -p models/staging models/sources macros tests analyses assets')
os.system('echo "SELECT SOMEVALUE FROM SOME.TABLE;" > models/staging/somequery.sql')

with open('/root/.dbt/profiles.yml', 'r') as pro_file:
    for schema in re.findall(r'schema: ([a-zA-Z_\-]+)', pro_file.read(), flags = re.MULTILINE | re.IGNORECASE):
        os.system(f"dbt run-operation generate_source --args 'schema_name: {schema}' > /workspaces/dbt-project-quickstart/{schema}.yml")
        with open(f'/workspaces/dbt-project-quickstart/{schema}.yml', 'r') as sources:
            for result in re.findall(r'(version: 2(.*\s)+)', sources.read(), flags = re.MULTILINE | re.IGNORECASE):
                os.system(f'echo "AUTOGENERATED DOCUMENTATION" /workspaces/dbt-project-quickstart/models/sources/{schema}.yml')
                with open(f'/workspaces/dbt-project-quickstart/models/sources/{schema}.yml', 'w') as yml_file:
                    yml_file.write(result[0])
        #os.system(f'mkdir -p /workspaces/dbt-project-quickstart/models/staging/{schema}')
        os.system(f'dbt-generator generate -s /workspaces/dbt-project-quickstart/models/sources/{schema}.yml -o /workspaces/dbt-project-quickstart/models/staging/{schema}')

print('For more info on how to proceed from here, visit https://courses.getdbt.com/courses/fundamentals')
