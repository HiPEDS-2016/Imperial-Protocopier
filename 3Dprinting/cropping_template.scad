height=0.3099240363;
radius=0.4746774538/2;
cprecent=90;
stlname="mug3_poisson.stl";
translate_vec=[ 0.0039832,   0.03925217,  0.28251162];
rotate_vec=[-0.99657955, -0.082639, 0.0];
rotate_deg=-76.3651804459;
scaling=100;


intersection() {
	rotate(rotate_vec*rotate_deg)
	scale([scaling, scaling, scaling]) 
	translate(translate_vec)
	import(stlname, convexity=3);

	translate([0,0,0.5]) 
	cylinder(h = height*scaling, r1 = radius*scaling*(cprecent/100), r2 = radius*scaling*(cprecent/100));
}




