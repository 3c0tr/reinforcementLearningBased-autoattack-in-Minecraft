package send_mesg2;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.PrintStream;
import java.net.ServerSocket;
import java.net.Socket;

public class PYserver {
    ClientHandler clientHandler;
    public boolean inited = false;
    private static String message;
    public void init(String[] args) throws IOException{
        ServerSocket server = new ServerSocket(2000);

        Socket client = server.accept();
        clientHandler = new ClientHandler(client);
        inited = true;
    }

    public void send(String str) throws IOException{
        message = str;
        this.clientHandler.run();
    }
    private static class ClientHandler extends Thread{
        private Socket socket;
        int cnt = 0;
        ClientHandler(Socket socket){
            this.socket = socket;
        }

        @Override
        public void run(){
            super.run();

            try{
                PrintStream socketOutput = new PrintStream(socket.getOutputStream());
                BufferedReader socketInput = new BufferedReader(new InputStreamReader(socket.getInputStream()));

                socketOutput.println(message);

            }catch(Exception e){
                System.out.println("连接异常");
            }
        }
    }
}