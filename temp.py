
jamal = ["hello", "hello 2"]


print('Press \033[1;44m ENTER \033[0m to go back to main menu\n')

for i, thing in enumerate(jamal, 1):
    print(f'{i} {thing}')