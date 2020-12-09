import argparse

parser = argparse.ArgumentParser(description='GPU resource monitoring.')
parser.add_argument(
    '-host', '--mail_host', type=str,
    help='set SMTP server, for example, smtp.xxx.com.')
parser.add_argument(
    '-user', '--mail_user', type=str,
    help='sender username, for example, xxx@xxx.com.')
parser.add_argument(
    '-pass', '--mail_pass', type=str,
    help='password.')
parser.add_argument(
    '--receivers', type=str, nargs='+',
    help='receivers.')
args = parser.parse_args()

content = args.mail_host + '\n' + args.mail_user + '\n' + args.mail_pass
for receiver in args.receivers:
    content += '\n' + receiver
with open("config.txt", "w") as f:
    f.write(content)

print("config file has been initialized successfully!")