import socket
import os
import webbrowser

HOST = "127.0.0.1"
FILE_SIZE = 10240  # 10 MB
CHUNK_SIZE = 100


def CreateServer(host, port):  # Create server
    Server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    Server.bind((host, port))
    Server.listen(5)
    return Server


def ReadRequest(Client):  # Read HTTP Request
    re = ""
    Client.settimeout(0.5)
    try:
        re = Client.recv(FILE_SIZE).decode()
        while re:
            re = re + Client.recv(FILE_SIZE).decode()
    except socket.timeout:  # fail after 0.4 second of no activity
        if not re:
            print("Didn't receive data! [Timeout]")
    finally:
        return re


def ReadHTTPRequest(Server):  # Client connect Server
    re = ""
    while re == "":
        Client, address = Server.accept()
        print("Client: ", address, " connected to Server")
        re = ReadRequest(Client)
    return Client, re


def PrintRequest_Response(Re, Type, FileHTML=""):
    print("----------------HTTP " + Type + " " + FileHTML + ": ")
    print(Re)


def MovePageHTML(Server, Client, port, fileHTML):  # Move to HTML page
    header = "HTTP/1.1 301 Moved Permanently"
    header += "\nLocation: http://127.0.0.1:" + str(port) + "/" + fileHTML
    header += "\n\n"
    PrintRequest_Response(header, "Response", fileHTML)
    Client.send(bytes(header, "utf-8"))
    Server.close()


def SendImg(Client, NameImg):  # send Image
    with open(NameImg, "rb") as f:
        L = f.read()
        header = "HTTP/1.1 200 OK"
        header += "\nContent-Type: text/html; charset=UTF-8"
        header += "\nContent-Encoding: UTF-8"
        header += "\nContent-Length: %d" % len(L)
        header += "\n\n"

    PrintRequest_Response(header, "Response")

    header = bytes(header, "utf-8") + L
    Client.send(header)


def SendPageImg(
    Server, Client, port, FileHTML, Request=""
):  # Send all image of file HTML
    if port != 8080:
        Server = CreateServer(HOST, port)
        Client, Request = ReadHTTPRequest(Server)

    PrintRequest_Response(Request, "Request")
    header = "GET /" + FileHTML + " HTTP/1.1"
    if header in Request:
        SendFileHTML(Client, FileHTML)
    Server.close()

    Server = CreateServer(HOST, port)

    if port == 1010:
        picName = ["SantaClaus3.png", "background.jpg"]
        num = 2
    elif port == 7070:
        picName = ["SantaClaus2.png", "background.jpg"]
        num = 2
    elif port == 8080:
        picName = ["LogoFIT.png", "SantaClaus.png", "background.jpg"]
        num = 3
    elif port == 9090:
        picName = [
            "SantaClaus4.png",
            "19127422-Huy.jpg",
            "19127525-Quan.jpg",
            "HCMUS_logo.png",
            "background.jpg",
        ]
        num = 5

    i = 0
    while i < num:
        Client, Request = ReadHTTPRequest(Server)
        PrintRequest_Response(Request, "Request")
        for pic in picName:
            if pic in Request:
                SendImg(Client, "./Pic/" + pic)
        i += 1

    Server.close()


def SendFileHTML(Client, FileName):  # server Response request HTTP success of unsuccess
    f = open(FileName, "rb")
    L = f.read()
    if FileName == "404.html":
        header = "HTTP/1.1 404 Not Found"
    else:
        header = "HTTP/1.1 200 OK"

    header += "\nContent-Type: text/html; charset=UTF-8"
    header += "\nContent-Encoding: UTF-8"
    header += "\nContent-Length: %d" % len(L)
    header += "\n\n"

    PrintRequest_Response(header, "Response", FileName)
    header += L.decode()
    Client.send(bytes(header, "utf-8"))


def MovePage(Server, Client, port, FileHTML):
    MovePageHTML(Server, Client, port, FileHTML)
    SendPageImg(Server, Client, port, FileHTML)


def Check(Request, re):  # check Password or check move to page Download
    if "POST / HTTP/1.1" not in Request:
        return False
    if re == "Password":
        if "Username=admin&Password=admin" in Request:
            return True

    elif re == "Download":
        if "btn=Download+file" in Request:
            return True

    return False


def SendFile(Client, FileName):  # server send file for client by Content Length
    with open(FileName, "rb") as f:
        L = f.read()

        header = "HTTP/1.1 200 OK"
        header += "\nContent-Disposition: attachment; filename=" + os.path.basename(
            FileName
        )
        header += "\nContent-Length: %d" % len(L)
        header += "\nConnection: close"
        header += "\n\n"
    PrintRequest_Response(header, "Response")
    header = bytes(header, "utf-8") + L
    Client.send(header)


def DownLoad(Server, Client, Request):
    file = [
        "Lorem_text.txt",
        "background.jpg",
        "Project_Socket_Programming_112020.pdf",
        "19127422_19127525.pdf",
        "01_Ethernet_Fundamentals.ppt",
        "HoaNoKhongMauAcoustic-HoaiLam.mp3",
        "Hoa_No_Khong_Mau.mp4",
    ]
    for f in file:
        if f in Request:
            SendFile(Client, "./Download/" + f)
            return True


if __name__ == "__main__":  # main function
    while True:
        print("Phan 1: tra ve trang chu khi truy cap Server")
        while True:
            # 1. Create Server Socket
            Server = CreateServer(HOST, 8080)
            # 2. Client connect Server + 3. Read HTTP Request
            Client, Request = ReadHTTPRequest(Server)
            PrintRequest_Response(Request, "Request")
            # 4. Send HTTP Response  + 5. Close Server
            temp = Request
            string_list = temp.split(" ")
            file = string_list[1].lstrip("/")

            if file != "index.html":
                MovePage(Server, Client, 7070, "404.html")
            else:
                SendFileHTML(Client, "index.html")
                SendPageImg(Server, Client, 8080, "index.html", Request)
                break
        # 1. Create Server Socket
        Server = CreateServer(HOST, 10000)
        # 2. Client connect Server + 3. Read HTTP Request
        Client, Request = ReadHTTPRequest(Server)
        PrintRequest_Response(Request, "Request")
        # check password va username nhap vao
        if Check(Request, "Password") == True:
            MovePage(Server, Client, 9090, "info.html")
            Server = CreateServer(HOST, 6060)
            # 2. Client connect Server + 3. Read HTTP Request
            Client, Request = ReadHTTPRequest(Server)
            PrintRequest_Response(Request, "Request")
            if Check(Request, "Download") == True:
                MovePage(Server, Client, 1010, "files.html")
                # download file
                while True:
                    Request = ""
                    Server = CreateServer(HOST, 2020)
                    Client, Request = ReadHTTPRequest(Server)
                    PrintRequest_Response(Request, "Request")
                    DownLoad(Server, Client, Request)
                    Server.close()
        else:
            MovePage(Server, Client, 7070, "404.html")
