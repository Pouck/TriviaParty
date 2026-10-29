$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Drawing
$sourceCode = @'
using System;
using System.Collections.Generic;
using System.Drawing;
using System.Drawing.Imaging;
using System.Runtime.InteropServices;
public static class CheckerboardCleaner {
    static bool IsBg(byte[] p, int i) {
        int b=p[i], g=p[i+1], r=p[i+2];
        return r>188 && g>188 && b>188 && Math.Max(r,Math.Max(g,b))-Math.Min(r,Math.Min(g,b))<22;
    }
    public static void Clean(string inputPath, string outputPath) {
        using(Bitmap original=new Bitmap(inputPath))
        using(Bitmap work=new Bitmap(original.Width,original.Height,PixelFormat.Format32bppArgb)) {
            int w=work.Width,h=work.Height; using(Graphics g=Graphics.FromImage(work)) g.DrawImage(original,0,0,w,h);
            Rectangle rect=new Rectangle(0,0,w,h); BitmapData data=work.LockBits(rect,ImageLockMode.ReadWrite,PixelFormat.Format32bppArgb);
            int stride=data.Stride; byte[] pixels=new byte[stride*h]; Marshal.Copy(data.Scan0,pixels,0,pixels.Length);
            bool[] seen=new bool[w*h]; Queue<int> q=new Queue<int>();
            Action<int,int> add=(x,y)=>{int n=y*w+x;if(!seen[n]&&IsBg(pixels,y*stride+x*4)){seen[n]=true;q.Enqueue(n);}};
            for(int x=0;x<w;x++){add(x,0);if(h>1)add(x,h-1);} for(int y=1;y<h-1;y++){add(0,y);if(w>1)add(w-1,y);}
            while(q.Count>0){int n=q.Dequeue(),x=n%w,y=n/w; if(x>0)add(x-1,y);if(x+1<w)add(x+1,y);if(y>0)add(x,y-1);if(y+1<h)add(x,y+1);}
            for(int y=0;y<h;y++) for(int x=0;x<w;x++) if(seen[y*w+x]) pixels[y*stride+x*4+3]=0;
            Marshal.Copy(pixels,0,data.Scan0,pixels.Length); work.UnlockBits(data); work.Save(outputPath,ImageFormat.Png);
        }
    }
}
'@
Add-Type -TypeDefinition $sourceCode -ReferencedAssemblies 'System.Drawing'
$dir = (Resolve-Path 'build/image-qsj-sampler/candidates/asterix-color').Path
$pairs = @(
    @('obelix-comic.jpg','obelix-color.png'),
    @('idefix-color.png','idefix-color-clean.png'),
    @('panoramix-color.png','panoramix-color-clean.png')
)
foreach ($pair in $pairs) {
    [CheckerboardCleaner]::Clean((Join-Path $dir $pair[0]),(Join-Path $dir $pair[1]))
    Write-Output "$($pair[0]) -> $($pair[1])"
}
