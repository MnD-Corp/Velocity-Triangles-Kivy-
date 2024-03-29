from kivy.config import Config
from kivy.core.window import Window
from kivy.properties import ObjectProperty,NumericProperty,StringProperty
from kivy.uix.screenmanager import ScreenManager, Screen
from math import radians, cos, sin
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.app import MDApp
from solver_if import system_if, system_X
from all_popups import firstPopup, secondPopup, thirdPopup, rpmPopup, h2tPopup, diamPopup, error_Popup
from computing_arrows import arrows
from Camber import cambers, mid_cambers
from Draw_functions import drawing_triangles, calculating_variables
from kivy.garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg
from kivy.app import App
import config as cf
from kivy.uix.boxlayout import BoxLayout
import matplotlib.pyplot as plt
from kivy.clock import Clock
from kivy_garden.graph import Graph, MeshLinePlot
from numpy import linspace
from kivy.lang import Builder

###########################################################################################
# from kivy.lang import Builder

Charts_list = []


class VelocityTriangles(Screen):

	########## Window properties #########
	Config.set('graphics', 'resizable', True)
	Window.size = (400, 700)
	Window.softinput_mode = "below_target"

	check = NumericProperty(0)

	n = ObjectProperty(None)
	l = NumericProperty(0)
	k = NumericProperty(0) #### Debugging tool for less than 3 variables and for not changing window ######
	t = NumericProperty(0) ##### Debugging tool for more than 3 variables ####
	graph_test = ObjectProperty(None)

	#### Values of checkboxes state ##########
	ch1_value = ObjectProperty('down')
	ch2_value = ObjectProperty('normal')
	ch3_value = ObjectProperty('normal')
	ch4_value = ObjectProperty('down')
	ch5_value = ObjectProperty('normal')

	def systemsolver(self):
		cf.graph_test = self.graph_test
		try:
			global a1e
			global a2e
			global b1e
			global b2e
			global pe
			global fe
			global rne
			global i

			pe = str(self.p.text)
			fe = str(self.f.text)
			rne = str(self.rn.text)
			a1e = str(self.a1.text)
			a2e = str(self.a2.text)
			a3e = str(self.a3.text)
			b1e = str(self.b1.text)
			b2e = str(self.b2.text)
			b3e = str(self.b3.text)

			if a1e == '':
				a1e = a3e
			if b1e == '':
				b1e = b3e

			global D1e
			global D2e
			global D3e
			global Rh1e
			global Rh2e
			global Rh3e
			global Ne

			D1e = str(self.d1.text)
			D2e = str(self.d2.text)
			D3e = str(self.d3.text)
			Rh1e = str(self.rh2t1.text)
			Rh2e = str(self.rh2t2.text)
			Rh3e = str(self.rh2t3.text)
			Ne = str(self.n.text)

			##################   System_Solver  ################
			pe, fe, rne, a1e, a2e, b1e, b2e, self.k, t, X, flag = system_if(pe, fe, rne, a1e, a2e, b1e, b2e)

			self.manager.get_screen('res_sc').XText = X
			self.manager.get_screen('simple').XText = X
			self.manager.get_screen('res_sc').flagText = flag

			############################# Drawing Triangles ######################################
			global U
			global x0
			global y0
			global x1
			global y1

			x0,y0 = Window.size[0]*130/400,Window.size[1]*70/700
			x1,y1 = Window.size[0]*270/400,Window.size[1]*70/700
			U = x1-x0
			xL = x1 - U*float(rne)-U*float(pe)/2
			yL = y0 + U*float(fe)
			xR = x1 - U*float(rne) +U*float(pe)/2
			yR = y0 + U*float(fe)

	######### While functions for triangles fitting #########
			while xL < self.x + Window.size[0]*60/400 or xR > self.width - Window.size[0]*80/400 or yL > Window.size[1]*200/700\
					or xR < self.x + Window.size[0]*60/400 or xL > self.width - Window.size[0] * 80 / 400:

				x0 = x0 + 1
				x1 = x1 - 1

				U = x1 - x0
				xL = x1 - U * float(rne) - U * float(pe) / 2
				yL = y0 + U * float(fe)
				xR = x1 - U * float(rne) + U * float(pe) / 2
				yR = y0 + U * float(fe)

			xL1u, yL1u, xL1d, yL1d, xL2u, yL2u, xL2d, yL2d, xR1u, yR1u, xR1d, yR1d, xR2u, yR2u, xR2d, yR2d = arrows(x0,y0,x1,y1,a1e,a2e,b1e,b2e)

			######################### Choosing if it is Turbine or Compressor ###################
			global tc
			if self.ch1_value == 'down':
				tc = 0  # turbine
				tc_namem = 'Turbine Middle'
			elif self.ch2_value == 'down':
				tc = 1  # compressor
				tc_namem = 'Compressor Middle'
			else:
				if float(pe) > 0.999:
					if abs(x1-xL)>abs(x1-xR):
						tc = 0  # turbine
						tc_namem = 'Turbine Middle'
					else:
						tc = 1  # compressor
						tc_namem = 'Compressor Middle'
				else:
					if abs(x1 - xL) > abs(x1 - xR):
						tc = 1  # compressor
						tc_namem = 'Compressor Middle'
					else:
						tc = 0  # turbine
						tc_namem = 'Turbine Middle'


			######################  Mid Camber line drawing ##################################
			xs_cent, ys_cent, xRm_camb, yRm_camb, yLm_camb, xLm_camb, yLm_rotor, yRm_rotor = mid_cambers(U, fe, rne, pe,
																										 y0, tc)

			#############################################################################################


			# create_database_nd(pe, fe, rne, a1e, a2e, b1e, b2e, tc)

#####################  Checking if the second compartment is completed ####################
			if D1e == '' and D2e == '' and D3e == '' and Rh1e == '' and Rh2e == '' and Rh3e == '' and Ne == '':
				self.check = 1
			else:
				self.check = 0
############################################################################################

################ Case of  Both Compartments filled #########################################
			if self.check == 0:
				############### Passing the Results on the Second Screen  ####################

				################ MID segment variables ##########################
				self.manager.get_screen('res_sc').pText = pe
				self.manager.get_screen('res_sc').fText = fe
				self.manager.get_screen('res_sc').rnText = rne
				self.manager.get_screen('res_sc').a1Text = str(-float(a1e))
				self.manager.get_screen('res_sc').a2Text = a2e
				self.manager.get_screen('res_sc').a3Text = a3e
				self.manager.get_screen('res_sc').b1Text = str(-float(b1e))
				self.manager.get_screen('res_sc').b2Text = b2e
				self.manager.get_screen('res_sc').b3Text = b3e


				############### Passing the Triangles Points on the Second Screen  ##################
				self.manager.get_screen('res_sc').x0Text = x0
				self.manager.get_screen('res_sc').y0Text = (y0)
				self.manager.get_screen('res_sc').x1Text = (x1)
				self.manager.get_screen('res_sc').y1Text = (y1)
				self.manager.get_screen('res_sc').UText = (U)
				self.manager.get_screen('res_sc').xLText = (xL)
				self.manager.get_screen('res_sc').yLText = (yL)
				self.manager.get_screen('res_sc').xRText = (xR)
				self.manager.get_screen('res_sc').yRText = (yR)

				############### Passing the Arrow Points on the Second Screen  ##################
				self.manager.get_screen('res_sc').xL1uText = (xL1u)
				self.manager.get_screen('res_sc').yL1uText = (yL1u)
				self.manager.get_screen('res_sc').xL1dText = (xL1d)
				self.manager.get_screen('res_sc').yL1dText = (yL1d)

				self.manager.get_screen('res_sc').xL2uText = (xL2u)
				self.manager.get_screen('res_sc').yL2uText = (yL2u)
				self.manager.get_screen('res_sc').xL2dText = (xL2d)
				self.manager.get_screen('res_sc').yL2dText = (yL2d)

				self.manager.get_screen('res_sc').xR1uText = (xR1u)
				self.manager.get_screen('res_sc').yR1uText = (yR1u)
				self.manager.get_screen('res_sc').xR1dText = (xR1d)
				self.manager.get_screen('res_sc').yR1dText = (yR1d)

				self.manager.get_screen('res_sc').xR2uText = (xR2u)
				self.manager.get_screen('res_sc').yR2uText = (yR2u)
				self.manager.get_screen('res_sc').xR2dText = (xR2d)
				self.manager.get_screen('res_sc').yR2dText = (yR2d)

				self.manager.get_screen('res_sc').yLm_cambText = (round(yLm_camb, 3))
				self.manager.get_screen('res_sc').xLm_cambText = (round(xLm_camb, 3))
				self.manager.get_screen('res_sc').ys_centText = (round(ys_cent, 3))
				self.manager.get_screen('res_sc').xs_centText = (round(xs_cent, 3))
				self.manager.get_screen('res_sc').yRm_cambText = (round(yRm_camb, 3))
				self.manager.get_screen('res_sc').xRm_cambText = (round(xRm_camb, 3))
				self.manager.get_screen('res_sc').yLm_rotorText = (round(yLm_rotor, 3))
				self.manager.get_screen('res_sc').yRm_rotorText = (round(yRm_rotor, 3))

				############### Passing the compressor or turbine text and possition on the Second Screen  ##################
				self.manager.get_screen('res_sc').tc_namemText = tc_namem

				############################################################################################

			################ Case of  the First Compartment filled #########################################
			else:
				############### Passing the Results on the Second Screen  ############################
				self.manager.get_screen('simple').pText = pe
				self.manager.get_screen('simple').fText = fe
				self.manager.get_screen('simple').rnText = rne
				self.manager.get_screen('simple').a1Text = str(-float(a1e))
				self.manager.get_screen('simple').a2Text = a2e
				self.manager.get_screen('simple').a3Text = a3e
				self.manager.get_screen('simple').b1Text = str(-float(b1e))
				self.manager.get_screen('simple').b2Text = b2e
				self.manager.get_screen('simple').b3Text = b3e

				############### Passing the Triangles Points on the Second Screen  ##################
				self.manager.get_screen('simple').x0Text = x0
				self.manager.get_screen('simple').y0Text = y0
				self.manager.get_screen('simple').x1Text = x1
				self.manager.get_screen('simple').y1Text = y1
				self.manager.get_screen('simple').UText = U
				self.manager.get_screen('simple').xLText = xL
				self.manager.get_screen('simple').yLText = yL
				self.manager.get_screen('simple').xRText = xR
				self.manager.get_screen('simple').yRText = yR

				############### Passing the Arrow Points on the Second Screen  ##################
				self.manager.get_screen('simple').xL1uText = xL1u
				self.manager.get_screen('simple').yL1uText = yL1u
				self.manager.get_screen('simple').xL1dText = xL1d
				self.manager.get_screen('simple').yL1dText = yL1d

				self.manager.get_screen('simple').xL2uText = xL2u
				self.manager.get_screen('simple').yL2uText = yL2u
				self.manager.get_screen('simple').xL2dText = xL2d
				self.manager.get_screen('simple').yL2dText = yL2d

				self.manager.get_screen('simple').xR1uText = xR1u
				self.manager.get_screen('simple').yR1uText = yR1u
				self.manager.get_screen('simple').xR1dText = xR1d
				self.manager.get_screen('simple').yR1dText = yR1d

				self.manager.get_screen('simple').xR2uText = xR2u
				self.manager.get_screen('simple').yR2uText = yR2u
				self.manager.get_screen('simple').xR2dText = xR2d
				self.manager.get_screen('simple').yR2dText = yR2d

				############### Passing the compressor or turbine text and possition on the Second Screen  ##################
				self.manager.get_screen('simple').tc_namemText = tc_namem

################ Debugging Section #################
			if self.k == 4:
				if float(b1e) - float(a1e) < 2 or float(a2e) - float(b2e) < 2:
					self.popup = secondPopup()
					self.k = 0

		except:
		########## It goes in to except if only variables are less than 3. So if is unnecesery #########
			X = system_X(pe,fe,rne,a1e,a2e,b1e,b2e)

			if X == [1,2,4,5] or X == [1,2,6,7] or X == [1, 2, 4, 7] or X == [1, 2, 5, 6] or X == [1, 3, 5, 7] or X == [1, 3, 4, 6]:
				error_Popup()
				self.k = 0
			else:
				firstPopup()
				self.k = 0  # mia allh timh oxi 4 gia na mhn allazei window

################          Dimendional Analisys           ################################
	def dml(self):

		try:
			global rh
			global rt
			global rm
			global Um
			global Uh
			global Ut
			global Vx
			global Vth1
			global Vth2
			global dvth

			if self.k != 0:
				if float(D1e) <= 0:
					self.popup = diamPopup()
					self.k = 0

				elif float(Rh1e) <= 0 or float(Rh1e) >= 1:
					self.popup = h2tPopup()
					self.k = 0


				elif float(Ne) <= 0:
					self.popup = rpmPopup()
					self.k = 0

			rt = float(D1e)/2
			rh = float(Rh1e)*rt
			rm = (rt+rh)/2

			Um = (1/60) * float(Ne) * rm

			Uh = (1/60) * float(Ne) * rh

			Ut = (1/60)* float(Ne) * rt

			Vx = float(fe)*Um

			dvth = float(pe)*Um

			V1 = Vx/cos(radians(float(a1e)))

			V2 = Vx/cos(radians(float(a2e)))

			W1 = Vx / cos(radians(float(b1e)))

			W2 = Vx / cos(radians(float(b2e)))

			Vth1 = -V1 * sin(radians(float(a1e)))
			Vth2 = V2 * sin(radians(float(a2e)))
			Wth1 = -W1 * sin(radians(float(b1e)))
			Wth2 = W2 * sin(radians(float(b2e)))


			#a3_calculation(round(Um,3),round(Vx,3),round(float(a1e),3))

			############### Passing the Results on the Second Screen  ##################
			self.manager.get_screen('res_sc').UmText = str(round(Um, 3))
			self.manager.get_screen('res_sc').VxText = str(round(Vx, 3))
			self.manager.get_screen('res_sc').V1Text = str(round(V1, 3))
			self.manager.get_screen('res_sc').V2Text = str(round(V2, 3))
			self.manager.get_screen('res_sc').W1Text = str(round(W1, 3))
			self.manager.get_screen('res_sc').W2Text = str(round(W2, 3))
			self.manager.get_screen('res_sc').DVthText = str(round(dvth, 3))
			self.manager.get_screen('res_sc').Vth1Text = str(round(Vth1, 3))
			self.manager.get_screen('res_sc').Vth2Text = str(round(Vth2, 3))
			self.manager.get_screen('res_sc').Wth1Text = str(round(Wth1, 3))
			self.manager.get_screen('res_sc').Wth2Text = str(round(Wth2, 3))


		except:
			if D1e == '' and D2e == '' and D3e == '' and Rh1e == '' and Rh2e == '' and Rh3e == '' and Ne == '':
				self.check = 1
			else:
				if self.k == 0:
					self.check = 1
				else:
					self.popup = thirdPopup()
					self.k = 0
					self.check = 1

#######################     Radial Balance  Computation   #######################
	def h2t_triangles(self):

		if self.ch3_value == 'normal' and self.ch3_value == 'normal' and self.ch3_value == 'normal':
			n = -1
		if self.ch3_value == 'down':
			n = 0
		if self.ch4_value == 'down':
			n = -1
		if self.ch5_value == 'down':
			n = 2

#######################################     Hub     ####################################################################

		########################  Calculating Hub variables #####################################

		Vth1h, Vth2h, Vx1h, Vx2h, dVthh, rneh, feh1, feh2, peh, Wth1h, Wth2h,\
		a1eh, a2eh, b1eh, b2eh, V1h, V2h, W1h, W2h = calculating_variables(n, Um, rne, Vth2, rh, rm, Vx, Uh)

		##########################     Drawing Hub Triangles       ###############################

		Uhp, x0h, x1h, xLh, yLh, xRh, yRh = drawing_triangles(Uh, Um, U, x0, y0, x1, Vth1h, Vth2h, feh1, feh2)

		##########################     Drawing Comparison Hub Triangles       ###############################

		Uhp_c, x0h_c, x1h_c, xLh_c, yLh_c, xRh_c, yRh_c = drawing_triangles(Uh, Um, U, x0, y0, x1, Vth1h, Vth2h, feh1, feh2)

		#####################  Hub Camber line drawing ##################################

		xs_cent, ys_cent, xRh_camb, yRh_camb, yLh_camb, xLh_camb, yLh_rotor, yRh_rotor = cambers(y0, Uhp_c, Uh, feh2,
																								 feh1, Vth1h, Vth2h,
																								 Wth1h, Wth2h,tc)

		# y_new = y0
		while xRh > self.width - Window.size[0] * 80 / 400 or xLh < self.x + Window.size[0] * 80 / 400 \
				or yLh > Window.size[1] * 200 / 700 or yRh > Window.size[1] * 200 / 700 \
				or xLh > self.width - Window.size[0] * 80 / 400 or xRh < self.x + Window.size[0] * 80 / 400:
			x0h = x0h + 1
			x1h = x1h - 1
			Uhp = x1h - x0h

			xLh = x1h - Uhp * float(rneh) - Uhp * float(peh) / 2
			yLh = y0 + Uhp * float(feh1)
			xRh = x1h - Uhp * float(rneh) + Uhp * float(peh) / 2
			yRh = y0 + Uhp * float(feh2)

		##########################     Drawing Hub Triangles Arrows      ###############################
		xL1uh, yL1uh, xL1dh, yL1dh, xL2uh, yL2uh, xL2dh, yL2dh, xR1uh, yR1uh, xR1dh, yR1dh, xR2uh, yR2uh,\
		xR2dh, yR2dh = arrows(x0h, y0, x1h, y1, a1eh, a2eh, b1eh, b2eh)

#######################################     TIP     ####################################################################

		########################  Calculating Tip variables #####################################

		Vth1t, Vth2t, Vx1t, Vx2t, dVtht, rnet, fet1, fet2, pet, Wth1t, Wth2t, a1et, a2et, b1et, b2et, V1t,\
		V2t, W1t, W2t = calculating_variables(n, Um, rne, Vth2, rt, rm, Vx, Ut)

		############################    Drawing  Tip Triangles    ##############################################

		Utp, x0t, x1t, xLt, yLt, xRt, yRt = drawing_triangles(Ut, Um, U, x0, y0, x1, Vth1t, Vth2t, fet1, fet2)

		############################    Drawing  Comparison Tip Triangles    ##############################################
		Utp_c, x0t_c, x1t_c, xLt_c, yLt_c, xRt_c, yRt_c = drawing_triangles(Ut, Um, U, x0, y0, x1, Vth1t, Vth2t, fet1, fet2)

		#####################  Tip Camber drawings ############

		xs_cent, ys_cent, xRt_camb, yRt_camb, yLt_camb, xLt_camb, yLt_rotor, yRt_rotor = cambers(y0, Utp_c, Ut, fet2,
																								 fet1, Vth1t, Vth2t,
																								 Wth1t, Wth2t,tc)

		while xRt > self.width - Window.size[0] * 80 / 400 or xLt < self.x + Window.size[0] * 80 / 400\
			or yLt > Window.size[1]*200/700 or yRt > Window.size[1]*200/700\
			or xLt > self.width - Window.size[0] * 80 / 400 or xRt < self.x + Window.size[0] * 80 / 400:
			x0t = x0t + 1
			x1t = x1t - 1
			Utp = x1t - x0t

			xLt = x1t - Utp * float(rnet) - Utp * float(pet) / 2
			yLt = y0 + Utp * float(fet1)
			xRt = x1t - Utp * float(rnet) + Utp * float(pet) / 2
			yRt = y0 + Utp * float(fet2)

		##########################     Drawing Tip Triangles Arrows      ###############################

		xL1ut, yL1ut, xL1dt, yL1dt, xL2ut, yL2ut, xL2dt, yL2dt, xR1ut, yR1ut, xR1dt, yR1dt, xR2ut, yR2ut,\
		xR2dt, yR2dt = arrows(x0t,y0,x1t,y1,a1et,a2et,b1et,b2et)


		############### Passing Hub Results #################
		self.manager.get_screen('res_sc').phText = str(round(peh, 3))
		self.manager.get_screen('res_sc').fh1Text = str(round(feh1, 3))
		self.manager.get_screen('res_sc').fh2Text = str(round(feh2, 3))
		self.manager.get_screen('res_sc').rnhText = str(round(rneh, 3))
		self.manager.get_screen('res_sc').a1hText = str(round(-a1eh, 3))
		self.manager.get_screen('res_sc').a2hText = str(round(a2eh, 3))
		self.manager.get_screen('res_sc').b1hText = str(round(-b1eh, 3))
		self.manager.get_screen('res_sc').b2hText = str(round(b2eh, 3))

		self.manager.get_screen('res_sc').UhText = str(round(Uh, 3))
		self.manager.get_screen('res_sc').Vx1hText = str(round(Vx1h, 3))
		self.manager.get_screen('res_sc').Vx2hText = str(round(Vx2h, 3))
		self.manager.get_screen('res_sc').V1hText = str(round(V1h, 3))
		self.manager.get_screen('res_sc').V2hText = str(round(V2h, 3))
		self.manager.get_screen('res_sc').W1hText = str(round(W1h, 3))
		self.manager.get_screen('res_sc').W2hText = str(round(W2h, 3))
		self.manager.get_screen('res_sc').DVthhText = str(round(dVthh, 3))
		self.manager.get_screen('res_sc').Vth1hText = str(round(Vth1h, 3))
		self.manager.get_screen('res_sc').Vth2hText = str(round(Vth2h, 3))
		self.manager.get_screen('res_sc').Wth1hText = str(round(Wth1h, 3))
		self.manager.get_screen('res_sc').Wth2hText = str(round(Wth2h, 3))

		####### Hub drawing variables #####
		self.manager.get_screen('res_sc').x0hText = (x0h)
		self.manager.get_screen('res_sc').x1hText = (x1h)
		self.manager.get_screen('res_sc').UhpText = (round(Uhp,3))
		self.manager.get_screen('res_sc').xLhText = (xLh)
		self.manager.get_screen('res_sc').yLhText = (yLh)
		self.manager.get_screen('res_sc').xRhText = (xRh)
		self.manager.get_screen('res_sc').yRhText = (yRh)

		#################    Hub  Arrows      ###############
		self.manager.get_screen('res_sc').xL1uhText = (xL1uh)
		self.manager.get_screen('res_sc').yL1uhText = (yL1uh)
		self.manager.get_screen('res_sc').xL1dhText = (xL1dh)
		self.manager.get_screen('res_sc').yL1dhText = (yL1dh)

		self.manager.get_screen('res_sc').xL2uhText = (xL2uh)
		self.manager.get_screen('res_sc').yL2uhText = (yL2uh)
		self.manager.get_screen('res_sc').xL2dhText = (xL2dh)
		self.manager.get_screen('res_sc').yL2dhText = (yL2dh)

		self.manager.get_screen('res_sc').xR1uhText = (xR1uh)
		self.manager.get_screen('res_sc').yR1uhText = (yR1uh)
		self.manager.get_screen('res_sc').xR1dhText = (xR1dh)
		self.manager.get_screen('res_sc').yR1dhText = (yR1dh)

		self.manager.get_screen('res_sc').xR2uhText = (xR2uh)
		self.manager.get_screen('res_sc').yR2uhText = (yR2uh)
		self.manager.get_screen('res_sc').xR2dhText = (xR2dh)
		self.manager.get_screen('res_sc').yR2dhText = (yR2dh)

		##################### Comparison window Hub triangles points ###############
		self.manager.get_screen('res_sc').x0h_cText = (round(x0h_c, 3))
		self.manager.get_screen('res_sc').x1h_cText = (round(x1h_c, 3))
		self.manager.get_screen('res_sc').xLh_cText = (round(xLh_c, 3))
		self.manager.get_screen('res_sc').yLh_cText = (round(yLh_c, 3))
		self.manager.get_screen('res_sc').xRh_cText = (round(xRh_c, 3))
		self.manager.get_screen('res_sc').yRh_cText = (round(yRh_c, 3))
		self.manager.get_screen('res_sc').Uhp_cText = (round(Uhp_c, 3))

		self.manager.get_screen('res_sc').ch3_value = self.ch3_value
		self.manager.get_screen('res_sc').ch4_value = self.ch4_value
		self.manager.get_screen('res_sc').ch5_value = self.ch5_value

		##################### Comparison window Hub camber points ###############
		self.manager.get_screen('res_sc').yLh_cambText = (round(yLh_camb, 3))
		self.manager.get_screen('res_sc').xLh_cambText = (round(xLh_camb, 3))
		self.manager.get_screen('res_sc').ys_centText = (round(ys_cent, 3))
		self.manager.get_screen('res_sc').xs_centText = (round(xs_cent, 3))
		self.manager.get_screen('res_sc').yRh_cambText = (round(yRh_camb, 3))
		self.manager.get_screen('res_sc').xRh_cambText = (round(xRh_camb, 3))
		self.manager.get_screen('res_sc').yRh_rotorText = (round(yRh_rotor, 3))
		self.manager.get_screen('res_sc').yLh_rotorText = (round(yLh_rotor, 3))


		############### Passing Tip Results #################
		self.manager.get_screen('res_sc').ptText = str(round(pet, 3))
		self.manager.get_screen('res_sc').ft1Text = str(round(fet1, 3))
		self.manager.get_screen('res_sc').ft2Text = str(round(fet2, 3))
		self.manager.get_screen('res_sc').rntText = str(round(rnet, 3))
		self.manager.get_screen('res_sc').a1tText = str(round(-a1et, 3))
		self.manager.get_screen('res_sc').a2tText = str(round(a2et, 3))
		self.manager.get_screen('res_sc').b1tText = str(round(-b1et, 3))
		self.manager.get_screen('res_sc').b2tText = str(round(b2et, 3))

		self.manager.get_screen('res_sc').UtpText = str(round(Utp,3))
		self.manager.get_screen('res_sc').UtText = str(round(Ut, 3))
		self.manager.get_screen('res_sc').Vx1tText = str(round(Vx1t, 3))
		self.manager.get_screen('res_sc').Vx2tText = str(round(Vx2t, 3))
		self.manager.get_screen('res_sc').V1tText = str(round(V1t, 3))
		self.manager.get_screen('res_sc').V2tText = str(round(V2t, 3))
		self.manager.get_screen('res_sc').W1tText = str(round(W1t, 3))
		self.manager.get_screen('res_sc').W2tText = str(round(W2t, 3))
		self.manager.get_screen('res_sc').DVthtText = str(round(dVtht, 3))
		self.manager.get_screen('res_sc').Vth1tText = str(round(Vth1t, 3))
		self.manager.get_screen('res_sc').Vth2tText = str(round(Vth2t, 3))
		self.manager.get_screen('res_sc').Wth1tText = str(round(Wth1t, 3))
		self.manager.get_screen('res_sc').Wth2tText = str(round(Wth2t, 3))

		##########   Drawing variables   ##########
		self.manager.get_screen('res_sc').x0tText = (x0t)
		self.manager.get_screen('res_sc').x1tText = (x1t)
		self.manager.get_screen('res_sc').xLtText = (xLt)
		self.manager.get_screen('res_sc').yLtText = (yLt)
		self.manager.get_screen('res_sc').xRtText = (xRt)
		self.manager.get_screen('res_sc').yRtText = (yRt)

		#################    Tip Arrows      ###############
		self.manager.get_screen('res_sc').xL1utText = (xL1ut)
		self.manager.get_screen('res_sc').yL1utText = (yL1ut)
		self.manager.get_screen('res_sc').xL1dtText = (xL1dt)
		self.manager.get_screen('res_sc').yL1dtText = (yL1dt)

		self.manager.get_screen('res_sc').xL2utText = (xL2ut)
		self.manager.get_screen('res_sc').yL2utText = (yL2ut)
		self.manager.get_screen('res_sc').xL2dtText = (xL2dt)
		self.manager.get_screen('res_sc').yL2dtText = (yL2dt)

		self.manager.get_screen('res_sc').xR1utText = (xR1ut)
		self.manager.get_screen('res_sc').yR1utText = (yR1ut)
		self.manager.get_screen('res_sc').xR1dtText = (xR1dt)
		self.manager.get_screen('res_sc').yR1dtText = (yR1dt)

		self.manager.get_screen('res_sc').xR2utText = (xR2ut)
		self.manager.get_screen('res_sc').yR2utText = (yR2ut)
		self.manager.get_screen('res_sc').xR2dtText = (xR2dt)
		self.manager.get_screen('res_sc').yR2dtText = (yR2dt)

		######################  Comparison window Tip triangle points #################
		self.manager.get_screen('res_sc').x0t_cText = (round(x0t_c, 3))
		self.manager.get_screen('res_sc').x1t_cText = (round(x1t_c, 3))
		self.manager.get_screen('res_sc').xLt_cText = (round(xLt_c, 3))
		self.manager.get_screen('res_sc').yLt_cText = (round(yLt_c, 3))
		self.manager.get_screen('res_sc').xRt_cText = (round(xRt_c, 3))
		self.manager.get_screen('res_sc').yRt_cText = (round(yRt_c, 3))
		self.manager.get_screen('res_sc').Utp_cText = (round(Utp_c, 3))

		###################### Comparison window tip camber points ##############
		self.manager.get_screen('res_sc').yLt_cambText = (round(yLt_camb, 3))
		self.manager.get_screen('res_sc').xLt_cambText = (round(xLt_camb, 3))
		self.manager.get_screen('res_sc').yRt_cambText = (round(yRt_camb, 3))
		self.manager.get_screen('res_sc').xRt_cambText = (round(xRt_camb, 3))
		self.manager.get_screen('res_sc').yRt_rotorText = (round(yRt_rotor, 3))
		self.manager.get_screen('res_sc').yLt_rotorText = (round(yLt_rotor, 3))

		self.chart_lists = [[rh, rm, rt], [Vx1h,Vx,Vx1t],[Vx2h,Vx,Vx2t],[Vth1h,Vth1,Vth1t],[Vth2h,Vth2,Vth2t],[dVthh,dvth,dVtht]]
		cf.chart_lists = self.chart_lists


class SimWindow(Screen):

	check = NumericProperty(0)

	tc_namemText = StringProperty('0')

	pText = StringProperty('0')
	fText = StringProperty('0')
	rnText = StringProperty('0')
	a1Text = StringProperty('0')
	a2Text = StringProperty('0')
	a3Text = StringProperty('0')
	b1Text = StringProperty('0')
	b2Text = StringProperty('0')
	b3Text = StringProperty('0')

	x0Text = NumericProperty(0)
	y0Text = NumericProperty(0)
	x1Text = NumericProperty(0)
	y1Text = NumericProperty(0)
	UText = NumericProperty(0)
	xLText = NumericProperty(0)
	yLText = NumericProperty(0)
	xRText = NumericProperty(0)
	yRText = NumericProperty(0)

	xL1uText = NumericProperty(0)
	yL1uText = NumericProperty(0)
	xL1dText = NumericProperty(0)
	yL1dText = NumericProperty(0)

	xL2uText = NumericProperty(0)
	yL2uText = NumericProperty(0)
	xL2dText = NumericProperty(0)
	yL2dText = NumericProperty(0)

	xR1uText = NumericProperty(0)
	yR1uText = NumericProperty(0)
	xR1dText = NumericProperty(0)
	yR1dText = NumericProperty(0)

	xR2uText = NumericProperty(0)
	yR2uText = NumericProperty(0)
	xR2dText = NumericProperty(0)
	yR2dText = NumericProperty(0)

	XText = ObjectProperty(0)

class Results(Screen):

	######### HUB ######
	check = NumericProperty(0)

	tc_namemText = StringProperty('0')

	phText = StringProperty('0')
	fh1Text = StringProperty('0')
	fh2Text = StringProperty('0')
	rnhText = StringProperty('0')
	a1hText = StringProperty('0')
	a2hText = StringProperty('0')
	b1hText = StringProperty('0')
	b2hText = StringProperty('0')

	UhText = StringProperty('0')
	UmText = StringProperty('1')
	Vx1hText = StringProperty('0')
	Vx2hText = StringProperty('0')
	V1hText = StringProperty('0')
	V2hText = StringProperty('0')
	W1hText = StringProperty('0')
	W2hText = StringProperty('0')
	DVthhText = StringProperty('0')
	Vth1hText = StringProperty('0')
	Vth2hText = StringProperty('0')
	Wth1hText = StringProperty('0')
	Wth2hText = StringProperty('0')

	y0Text = NumericProperty(0)
	y1Text = NumericProperty(0)
	x0hText = NumericProperty(0)
	x1hText = NumericProperty(0)
	UhpText = NumericProperty(0)
	UText = NumericProperty(0)
	xLhText = NumericProperty(0)
	yLhText = NumericProperty(0)
	xRhText = NumericProperty(0)
	yRhText = NumericProperty(0)

	xL1uhText = NumericProperty(0)
	yL1uhText = NumericProperty(0)
	xL1dhText = NumericProperty(0)
	yL1dhText = NumericProperty(0)

	xL2uhText = NumericProperty(0)
	yL2uhText = NumericProperty(0)
	xL2dhText = NumericProperty(0)
	yL2dhText = NumericProperty(0)

	xR1uhText = NumericProperty(0)
	yR1uhText = NumericProperty(0)
	xR1dhText = NumericProperty(0)
	yR1dhText = NumericProperty(0)

	xR2uhText = NumericProperty(0)
	yR2uhText = NumericProperty(0)
	xR2dhText = NumericProperty(0)
	yR2dhText = NumericProperty(0)

	tc_namehText = StringProperty('0')

	######### MID ######
	XText = ObjectProperty(0)
	pText = StringProperty('0')
	fText = StringProperty('0')
	rnText = StringProperty('0')
	a1Text = StringProperty('0')
	a2Text = StringProperty('0')
	a3Text = StringProperty('0')
	b1Text = StringProperty('0')
	b2Text = StringProperty('0')
	b3Text = StringProperty('0')

	x0Text = NumericProperty(0)
	x1Text = NumericProperty(0)
	xLText = NumericProperty(0)
	yLText = NumericProperty(0)
	xRText = NumericProperty(0)
	yRText = NumericProperty(0)   # idio me yLText (apalifi)

	UtText = StringProperty('0')
	VxText = StringProperty('0')
	V1Text = StringProperty('0')
	V2Text = StringProperty('0')
	W1Text = StringProperty('0')
	W2Text = StringProperty('0')

	DVthText = StringProperty('0')
	Vth1Text = StringProperty('0')
	Vth2Text = StringProperty('0')
	Wth1Text = StringProperty('0')
	Wth2Text = StringProperty('0')

	xL1uText = NumericProperty(0)
	yL1uText = NumericProperty(0)
	xL1dText = NumericProperty(0)
	yL1dText = NumericProperty(0)

	xL2uText = NumericProperty(0)
	yL2uText = NumericProperty(0)
	xL2dText = NumericProperty(0)
	yL2dText = NumericProperty(0)

	xR1uText = NumericProperty(0)
	yR1uText = NumericProperty(0)
	xR1dText = NumericProperty(0)
	yR1dText = NumericProperty(0)

	xR2uText = NumericProperty(0)
	yR2uText = NumericProperty(0)
	xR2dText = NumericProperty(0)
	yR2dText = NumericProperty(0)

	flagText = ObjectProperty(None)
	######### TIP ######
	ptText = StringProperty('0')
	ft1Text = StringProperty('0')
	ft2Text = StringProperty('0')
	rntText = StringProperty('0')
	a1tText = StringProperty('0')
	a2tText = StringProperty('0')
	b1tText = StringProperty('0')
	b2tText = StringProperty('0')
	Vx1tText = StringProperty('0')
	Vx2tText = StringProperty('0')
	V1tText = StringProperty('0')
	V2tText = StringProperty('0')
	W1tText = StringProperty('0')
	W2tText = StringProperty('0')
	DVthtText = StringProperty('0')
	Vth1tText = StringProperty('0')
	Vth2tText = StringProperty('0')
	Wth1tText = StringProperty('0')
	Wth2tText = StringProperty('0')

	x0tText = NumericProperty(0)
	x1tText = NumericProperty(0)
	UtpText = NumericProperty(0)
	xLtText = NumericProperty(0)
	yLtText = NumericProperty(0)
	xRtText = NumericProperty(0)
	yRtText = NumericProperty(0)

	xL1utText = NumericProperty(0)
	yL1utText = NumericProperty(0)
	xL1dtText = NumericProperty(0)
	yL1dtText = NumericProperty(0)

	xL2utText = NumericProperty(0)
	yL2utText = NumericProperty(0)
	xL2dtText = NumericProperty(0)
	yL2dtText = NumericProperty(0)

	xR1utText = NumericProperty(0)
	yR1utText = NumericProperty(0)
	xR1dtText = NumericProperty(0)
	yR1dtText = NumericProperty(0)

	xR2utText = NumericProperty(0)
	yR2utText = NumericProperty(0)
	xR2dtText = NumericProperty(0)
	yR2dtText = NumericProperty(0)

	tc_nametText = StringProperty('0')

######### Comp window triangles points #################

	############ Hub ##############
	x0h_cText = NumericProperty(0)
	x1h_cText = NumericProperty(0)
	xLh_cText = NumericProperty(0)
	yLh_cText = NumericProperty(0)
	xRh_cText = NumericProperty(0)
	yRh_cText = NumericProperty(0)
	Uhp_cText = NumericProperty(0)

	############ Tip ##############
	x0t_cText = NumericProperty(0)
	x1t_cText = NumericProperty(0)
	xLt_cText = NumericProperty(0)
	yLt_cText = NumericProperty(0)
	xRt_cText = NumericProperty(0)
	yRt_cText = NumericProperty(0)
	Utp_cText = NumericProperty(0)

	ch3_value = StringProperty('normal')
	ch4_value = StringProperty('normal')
	ch5_value = StringProperty('normal')

######## Camber Line points ##################
	yLh_cambText = NumericProperty(0)
	xLh_cambText = NumericProperty(0)
	xs_centText = NumericProperty(0)
	ys_centText = NumericProperty(0)
	yRh_cambText = NumericProperty(0)
	xRh_cambText = NumericProperty(0)

	yLt_cambText = NumericProperty(0)
	xLt_cambText = NumericProperty(0)
	yRt_cambText = NumericProperty(0)
	xRt_cambText = NumericProperty(0)

	yLm_cambText = NumericProperty(0)
	xLm_cambText = NumericProperty(0)
	yRm_cambText = NumericProperty(0)
	xRm_cambText = NumericProperty(0)

	yRh_rotorText = NumericProperty(0)
	yLh_rotorText = NumericProperty(0)
	yRt_rotorText = NumericProperty(0)
	yLt_rotorText = NumericProperty(0)
	yRm_rotorText = NumericProperty(0)
	yLm_rotorText = NumericProperty(0)

	########### Charts Window ########

	chart1 = ObjectProperty(None)
	chart2 = ObjectProperty(None)
	chart3 = ObjectProperty(None)

	def draw_charts(self):

		# self.chart_lists = [[rh, rm, rt], [Vx1h,Vx,Vx1t],[Vx2h,Vx,Vx2t],[Vth1h,Vth1,Vth1t],[Vth2h,Vth2,Vth2t],[dVthh,dvth,dVtht]]
		# cf.chart_lists = self.chart_lists

		plt.clf()

		plt.title("Axial Velocities Vx", fontsize=12)
		plt.ylabel(" r [m]", fontsize=10)
		plt.xlabel(" V\u2093 [m/s]", fontsize=10)
		plt.tight_layout(pad=0.7)
		plt.plot(cf.chart_lists[1], cf.chart_lists[0])
		plt.plot(cf.chart_lists[2], cf.chart_lists[0])
		plt.legend(["V\u2093\u2081", "V\u2093\u2082"])

		self.chart1.figure = plt.gcf()
		self.chart1.draw()

		plt.clf()

		plt.title("Tangential Velocities Vθ", fontsize=12)
		plt.ylabel(" r [m]", fontsize=10)
		plt.xlabel(" Vθ [m/s]", fontsize=10)
		plt.plot(cf.chart_lists[3], cf.chart_lists[0])
		plt.plot(cf.chart_lists[4], cf.chart_lists[0])
		plt.legend(["Vθ\u2081", "Vθ\u2082"])
		self.chart2.figure = plt.gcf()
		self.chart2.draw()


		plt.clf()

		plt.title("Diferrence in tangential velocities ΔVθ", fontsize=12)
		plt.ylabel(" r [m]", fontsize=10)
		plt.xlabel(" ΔVθ [m/s]", fontsize=10)

		plt.plot(cf.chart_lists[5], cf.chart_lists[0])

		plt.legend(["ΔVθ"])
		self.chart3.figure = plt.gcf()
		self.chart3.draw()

class InfoScreen(Screen):
	pass

class MyFigure(FigureCanvasKivyAgg):
	def __init__(self, **kwargs):
		super().__init__(plt.gcf(), **kwargs)

class WindowManager(ScreenManager):
	pass

class MainApp(MDApp):
	# res = Results()
	def __init__(self, **kwargs):
		self.title = "VTA"
		self.theme_cls.theme_style = "Light"
		self.theme_cls.primary_palette = "DeepOrange"
		self.theme_cls.secondary_palette = "Black"
		super().__init__(**kwargs)

MainApp().run()



