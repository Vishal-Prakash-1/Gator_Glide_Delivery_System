import sys
import re
from order_management_system import OrderManagementSystem


if len(sys.argv) < 2:
    print("Usage: python program.py input_file.txt")
    sys.exit(1)

input_file = sys.argv[1]
output_file = input_file.split('.')[0] + "_output_file.txt"

order_management_system = OrderManagementSystem()

with open(input_file, 'r') as f:
    lines = f.readlines()

with open(output_file, 'w') as f:
    for line in lines:
        line = line.strip()
        match = re.match(r'(\w+)\((.*?)\)', line)
        if match:
            function_name = match.group(1)
            if function_name == "Quit":
                output = order_management_system.quit()
            else:
                args = match.group(2).split(',')
                args = [int(arg.strip()) for arg in args]
                if function_name == "createOrder":
                    output = order_management_system.create_order(*args)
                elif function_name == "cancelOrder":
                    output = order_management_system.cancel_order(*args)
                elif function_name == "print":
                    if len(args) == 2:
                        output = order_management_system.print_orders(*args)
                    else:
                        output = order_management_system.print_order(*args)
                elif function_name == "getRankOfOrder":
                    output = order_management_system.get_rank_of_order(*args)
                elif function_name == "updateTime":
                    output = order_management_system.update_time(*args)

            f.write('\n'.join(output) + '\n')