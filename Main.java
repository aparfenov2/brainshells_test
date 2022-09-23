import java.io.File;
import java.util.Enumeration;
import java.util.ArrayList;
import java.util.List;
import java.util.zip.ZipEntry;
import java.util.zip.ZipFile;
import java.awt.image.BufferedImage;
import javax.imageio.ImageIO;
import java.io.IOException;

class Main {
    static double calculateEuclideanDistance(double[] a, double[] b) {
        double innerSum = 0.0;
        for (int i = 0; i < a.length; i++) {
            innerSum += Math.pow(a[i] - b[i], 2.0);
        }
        return Math.sqrt(innerSum);
    }

    // normalize image for each R,G,B channel to range 0..1
    static double[] normalizeImage(int[] image, boolean[] isBlack) {
        double[] ret = new double[image.length];
        int minI[] = new int[]{1000, 1000, 1000};
        int maxI[] = new int[]{0, 0, 0};
        int blackThd = 40;
        for (int i=0; i < image.length; i++) {
            if (minI[i % 3] > ((byte)image[i] & 0xff)) {
                minI[i % 3] = ((byte)image[i] & 0xff);
            }
            if (maxI[i % 3] < ((byte)image[i] & 0xff)) {
                maxI[i % 3] = ((byte)image[i] & 0xff);
            }
        }
        isBlack[0] = true;
        for (int i=0; i<3; i++) {
            if (maxI[i] - minI[i] > blackThd) {
                isBlack[0] = false;
            }
        }
        for (int i=0; i < image.length; i++) {
            ret[i] = (double)((int)((byte)image[i] & 0xff) - minI[i % 3]) / (double)(maxI[i % 3] - minI[i % 3]);
        }
        return ret;
    }

    // finds minimum euclidean distance between images
    static double findNearestDist(List<double []> gallery, double[] query, int[] minDistId) {
        minDistId[0] = -1;
        double minDist = 1e9;
        for (int i=0; i<gallery.size(); i++) {
            double dist = Main.calculateEuclideanDistance(gallery.get(i), query);
            if (dist < minDist) {
                minDistId[0] = i;
                minDist = dist;
                if (minDist <= 0) {
                    break;
                }
            }
        }
        return minDist;
    }

    public static void main(String[] args) throws IOException {
        if (args.length == 0) {
            System.out.println("usage: this.jar path_to_images_folder");
            return;
        }
        // load set of 25 cards
        ZipFile zip = new ZipFile("cards.zip");
        List<double []> cards = new ArrayList<double []>();
        List<String> cnames = new ArrayList<String>();

        for (Enumeration e = zip.entries(); e.hasMoreElements(); ) {
            ZipEntry entry = (ZipEntry) e.nextElement();
            String fileNameWithOutExt = entry.getName().replaceFirst("[.][^.]+$", "");
            BufferedImage image = ImageIO.read(zip.getInputStream(entry));
            int[] bytes = image.getRGB(0, 0, image.getWidth(), image.getHeight(), null, 0, image.getWidth());
            boolean[] isBlack = new boolean[]{false};
            cards.add(Main.normalizeImage(bytes, isBlack));
            cnames.add(fileNameWithOutExt);
        }
        for (File file : new File(args[0]).listFiles()) {
            if (file.isFile()) {
                // System.out.println(file.getName());
                BufferedImage image = ImageIO.read(file);
                int x1 = 147;
                int y1 = 590;
                int y2 = 670;
                double xstep = 71.66;
                int xwidth = 55;
                int maxCards = 5;
                // scan center of image, get individual cards
                List<String> ret = new ArrayList<String>();
                for (int cardNum=0; cardNum < maxCards; cardNum++ ) {
                    int xa = x1 + (int) (cardNum * xstep);
                    BufferedImage roi = image.getSubimage(xa, y1, xwidth, y2-y1);
                    int[] query = roi.getRGB(0, 0, roi.getWidth(), roi.getHeight(), null, 0, roi.getWidth());
                    boolean[] isBlack = new boolean[]{false};
                    double[] normalizedQuery = Main.normalizeImage(query, isBlack);
                    int[] minDistId = new int[1];
                    double minDist = Main.findNearestDist(cards, normalizedQuery, minDistId);
                    if (isBlack[0] || minDist > 20 || minDistId[0] < 0) {
                        // black image or not-a-card
                        break;
                    }
                    ret.add(cnames.get(minDistId[0]));
                }
                // print result for file
                StringBuilder disp = new StringBuilder();
                disp.append(file.getName());
                disp.append(" ");
                for(String cname:ret) {
                    disp.append(cname);
                }
                System.out.println(disp);
            }
        }
    }
}