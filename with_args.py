import dree


def main():
    dree.scan_dir(
        "./lambda/Checkout_Auditing_2024/top_2k/Dataset_2k_all", "lambda.json", "./descriptions.json")


if __name__ == "__main__":
    main()
