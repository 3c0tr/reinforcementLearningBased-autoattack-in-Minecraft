package send_mesg2;

import net.minecraft.client.Minecraft;
import net.minecraft.network.chat.Component;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.monster.Zombie;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.client.ClientCommandHandler;
import net.minecraftforge.client.event.InputEvent;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.entity.living.LivingDamageEvent;
import net.minecraftforge.event.entity.living.LivingDeathEvent;
import net.minecraftforge.event.entity.player.PlayerEvent;
import net.minecraftforge.event.entity.player.PlayerInteractEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.network.PlayMessages;

import java.io.IOException;
import java.util.Random;

@Mod("send_mesg2")
@Mod.EventBusSubscriber
public class send_mesg {
    static PYserver pyserver;
    static int zombie_cnt = 0;
    private static final int cnt = 1;

    @SubscribeEvent
    public static void playlogin(PlayerEvent.PlayerLoggedInEvent event) throws IOException{
        pyserver = new PYserver();
        pyserver.init(null);
        ClientCommandHandler.init();
    }

    @SubscribeEvent
    public static void getDeathInfo(LivingDeathEvent event) throws IOException {
        if(event.getEntity() != null && event.getSource().getEntity() != null) {
            if (event.getEntity().getDisplayName().getString().equals("Zombie")
                    && !event.getEntity().level.isClientSide()
                    && event.getSource().getEntity().getDisplayName().getString().equals("Dev")) {
                if (pyserver != null) {
                    pyserver.send("Zombie");
                }
                zombie_cnt += 1;
                if(zombie_cnt >= cnt) {
                    Minecraft.getInstance().player.commandSigned("kill @p", null);
                    zombie_cnt = 0;
                }
            }
        }
        if(event.getEntity().getDisplayName().getString().equals("Dev") && !event.getEntity().level.isClientSide()){
            if(pyserver != null) {
                pyserver.send("You");
            }
            //Minecraft.getInstance().player.commandSigned("kill @p", null);
        }
    }

    @SubscribeEvent
    public static void getDamageInfo(LivingDamageEvent event) throws IOException {
        if(pyserver != null) {
            if (event.getEntity().getDisplayName().getString().equals("Zombie") && !event.getEntity().level.isClientSide()) {
                System.out.println(event.getAmount());
                int pX = (int) event.getAmount();
                String posx;

                if (pX < 10) {
                    posx = "px:000" + Integer.toString(pX);
                } else if (pX < 100) {
                    posx = "px:00" + Integer.toString(pX);
                } else if (pX < 1000) {
                    posx = "px:0" + Integer.toString(pX);
                } else {
                    posx = "px:" + Integer.toString(pX);
                }
                if (pyserver != null) {
                    pyserver.send(posx);
                }
            }
            if (event.getEntity().getDisplayName().getString().equals(Minecraft.getInstance().player.getDisplayName().getString()) && !event.getEntity().level.isClientSide()) {
                System.out.println(event.getAmount());
                int pY = (int) event.getAmount();
                String posy;

                if (pY < 10) {
                    posy = "py:000" + Integer.toString(pY);
                } else if (pY < 100) {
                    posy = "py:00" + Integer.toString(pY);
                } else if (pY < 1000) {
                    posy = "py:0" + Integer.toString(pY);
                } else {
                    posy = "py:" + Integer.toString(pY);
                }
                if (pyserver != null) {
                    pyserver.send(posy);
                }
            }
        }
    }

    @SubscribeEvent
    public static void clearAllMobs(PlayerEvent.PlayerRespawnEvent event) throws IOException {
        pyserver.send("Respawn");
        Minecraft.getInstance().player.commandSigned("kill @e[name=Zombie]", null);
        for(int i = 0; i < cnt; i++) {
            Random random = new Random();
            int x = random.nextInt(11) - 2;
            int z = random.nextInt(1);
            String str = "summon minecraft:zombie " + Integer.toString(x) + " 23 -" + Integer.toString(z) + ".5";
            Minecraft.getInstance().player.commandSigned(str, null);
        }
        //Player player = Minecraft.getInstance().player;
        //player.sendSystemMessage(Component.literal("/kill @e[name=Zombie]"));
        //ClientCommandHandler.runCommand("kill @e[name=Zombie]");
    }
    /*
    @SubscribeEvent
    public static void leftClick(PlayerInteractEvent.LeftClickBlock event) throws IOException{
        if(Minecraft.getInstance().player.getLevel().isClientSide()) {
        Random random = new Random();
        int x = random.nextInt(11) - 2;
        int z = random.nextInt(1);
        String str = "summon minecraft:zombie " + Integer.toString(x) + " 23 -" + Integer.toString(z) + ".5";
        Minecraft.getInstance().player.commandSigned(str, null);
        }
    }*/

    @SubscribeEvent
    public static void onKeyPressed(InputEvent.Key event) {
        if(event.getKey() == 75){
            //Minecraft.getInstance().player.commandSigned("kill @p", null);
        }
    }

    @SubscribeEvent
    public static void always(TickEvent.PlayerTickEvent event) throws IOException{
        if(pyserver != null && pyserver.inited) {
            pyserver.send("#");
        }
        //Player player = Minecraft.getInstance().player;
        //int pX = (int)(player.getPosition(0).x*10) + 1000;
        //int pY = (int)(player.getPosition(0).z*10) + 1000;
        //int rX = (int)player.getRotationVector().x;
        //int rY = (int)player.getRotationVector().y;
        //rY = Math.abs(rY)%360;
        //rX = rX + 90;
        //String posx, posy, rotx, roty;
        /*
        if(pyserver.inited) {

            if(pX < 10) {
                posx = "px:000" + Integer.toString(pX);
            } else if (pX < 100) {
                posx = "px:00" + Integer.toString(pX);
            }else if (pX < 1000){
                posx = "px:0"+Integer.toString(pX);
            }else{
                posx = "px:"+Integer.toString(pX);
            }

            if(pY < 10) {
                posy = "py:000" + Integer.toString(pY);
            } else if (pY < 100) {
                posy = "py:00" + Integer.toString(pY);
            }else if (pY < 1000){
                posy = "py:0"+Integer.toString(pY);
            }else{
                posy = "py:"+Integer.toString(pY);
            }

            if(rX < 10) {
                rotx = "rx:00" + Integer.toString(rX);
            } else if (rX < 100) {
                rotx = "rx:0" + Integer.toString(rX);
            }else{
                rotx = "rx:"+Integer.toString(rX);
            }

            if(rY < 10) {
                roty = "ry:00" + Integer.toString(rY);
            } else if (rY < 100) {
                roty = "ry:0" + Integer.toString(rY);
            }else{
                roty = "ry:"+Integer.toString(rY);
            }
            pyserver.send(posx + posy + rotx + roty);
        }*/
    }
}
