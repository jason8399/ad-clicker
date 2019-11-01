class Cookies:

    def __init__(self, path: str):
        self.cookies = []
        self.source = ""
        self.file_path = path
        self.read()
        self.process()

    def read(self):
        with open(self.file_path, "r") as f:
            self.source = f.readline()

    def process(self):
        cookies_items = self.source.split("; ")
        for item in cookies_items:
            name, value = item.split("=", 1)
            self.cookies.append({
                "name": name,
                "value": value
            })

if __name__ == "__main__":
    cookies = Cookies("./cookies.txt")
    print(cookies.cookies)