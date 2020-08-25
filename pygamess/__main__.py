from ruamel.yaml import YAML
import argparse, subprocess
from . import gamess, email
parser = argparse.ArgumentParser("pyGamess command line interface")
parser.add_argument('input_file')
parser.add_argument('-n','--num_cores', default=None, type=int)
parser.add_argument('-x', '--executable_num', default='01', type=str)
parser.add_argument('-s', '--rungms_suffix', default='0', type=str)
parser.add_argument('-o', '--output_file', default=None, type=str)
parser.add_argument('-e', '--emails_yml', nargs="?", type=str)
args = parser.parse_args()
g = gamess.Gamess(rungms_suffix=args.rungms_suffix, executable_num=args.executable_num, num_cores=args.num_cores)
if args.output_file is None:
    output_file = args.input_file+".log"
else:
    output_file = args.output_file
status = g.run_input(args.input_file, output_file)
lastlinesrun = subprocess.run(f"tail -n 40 {output_file}", shell=True, stdout=subprocess.PIPE)
yaml = YAML(typ="safe")
with open(args.emails_yml, "r") as opf:
    configuration = yaml.load(opf)

if status == 0:
	email.smtplib_email(configuration["sucess"]["body"].format(output_file, lastlinesrun.stdout.decode("UTF-8")), configuration["sucess"]["receivers"],
		configuration["success"]["subject"], configuration["smtp"])
else:
	email.smtplib_email(configuration["error"]["body"].format(output_file, status, lastlinesrun.stdout.decode("UTF-8")), configuration["error"]["receivers"],
		configuration["error"]["subject"], configuration["smtp"])
