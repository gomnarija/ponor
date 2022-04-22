class Food(krcko.System):

    def setup(self):
        self.inspect_momo = krcko.Momo()
        self.inspect_momo.load(defs.MOM_DIR_PATH + "item_inspect.momo")

        self.eating_momo = krcko.Momo()
        self.eating_momo.load(defs.MOM_DIR_PATH + "eating.momo")




    def update(self):
        
        #food inspection detection
        if self.turn_machine.action_name == "INSPECT_ITEM":
            inspection_action = self.turn_machine.action
			#inspect only items with FOOD item_class
            if inspection_action.item_class == "FOOD":
                self.do_inspect(inspection_action.item_eid, inspection_action.amount)	

        #food eating detection
        if self.turn_machine.action_name == "EAT_FOOD":
            eating_action = self.turn_machine.action
            self.do_eat(eating_action.carrier_eid, eating_action.item_eid)




    def cleanup(self):
        pass


    def do_eat(self, carrier_eid :int, item_eid :int) -> None:
        '''
            Carrier eats food from his inventory.
        '''

        #carrier :: inventory, hunger
        if not self.scene.entity_has_component(carrier_eid, "inventory") or\
            not self.scene.entity_has_component(carrier_eid, "hunger"):
            #
            logging.error("failed to get carreir entity.")
            return
        #get carrier entity
        carrier_ent = self.scene.get_entity(carrier_eid)

        #carrier must have given item in her inventory
        if not item_eid in carrier_ent['inventory'].items:
            logging.error("Carrier doesn't have given item.")
            return 

        #item :: item, food
        if not self.scene.entity_has_component(item_eid, "item") or\
            not self.scene.entity_has_component(item_eid, "food"):
            #
            logging.error("failed to get item entity.")
            return           

        #get item entity
        item_ent = self.scene.get_entity(item_eid)


        #EAT IT 
        carrier_ent['hunger'].amount += item_ent['food'].nutrition
        carrier_ent['hunger'].amount = min(carrier_ent['hunger'].max_hunger, carrier_ent['hunger'].amount)

        #remove item from inventory
        drop_action			=	krcko.create_action("DROP_ITEM", [], ['carrier_eid', 'item_eid'], [carrier_eid, item_eid])
        self.turn_machine.insert_action(drop_action)

        #momo
        self.eating_momo.add_arguments({'name' : item_ent['item'].name})
        self.eating_momo.run(fields = ["ATE_DEFAULT"])

		#continue
        continue_key			    =	self.game.controls["MOMO"]["CONTINUE"]

		#momo form text
        text :str			        =	self.eating_momo.pick("ATE_DEFAULT")

		#momo action
        momo_action			        =	krcko.momo_info_action(text, continue_key) 

		#insert
        self.turn_machine.insert_action(momo_action)	





    def do_inspect(self, item_eid :int, amount :int) -> None:
        '''
            Momo form with food item information.
        '''

        #item, food
        if not self.scene.entity_has_component(item_eid, "item") or\
            not self.scene.entity_has_component(item_eid, "food"):
            #
            logging.error("failed to get food entity")
            return
        #get entity
        item_ent = self.scene.get_entity(item_eid)

		#momo
        self.inspect_momo.add_arguments({'name' : item_ent['item'].name,\
							'amount' : amount})
		#
        self.inspect_momo.run(fields=["FOOD", "OPTION_CONTINUE", "OPTION_DROP_ITEM", "OPTION_EAT_FOOD"])

		#player is carrier
        carrier_eid :int		=	self.scene.get_eid_from_name("player")	


		#continue option
        continue_action			    =	krcko.create_action("CONTINUE", [], [], [])
        continue_option_text :str	=	self.inspect_momo.pick("OPTION_CONTINUE")
        continue_key :str		    =	self.game.controls['MOMO']['CONTINUE']

        #eat option
        eat_action			        =	krcko.create_action("EAT_FOOD", [krcko.ActionFlag.ENDING],\
                                                             ["carrier_eid", "item_eid"],\
                                                                [carrier_eid, item_eid])
        eat_option_text :str	    =	self.inspect_momo.pick("OPTION_EAT_FOOD")
        eat_key :str		        =	self.game.controls['MOMO']['USE_ITEM']

    	#drop option	
        drop_action			    =	krcko.create_action("DROP_ITEM", [krcko.ActionFlag.ENDING], ['carrier_eid', 'item_eid'], [carrier_eid, item_eid])
        drop_option_text :str	=	self.inspect_momo.pick("OPTION_DROP_ITEM")
        drop_key :str			=	self.game.controls['MOMO']['DROP_ITEM']
		

	
		#momo form text
        info_text :str		=	self.inspect_momo.pick("FOOD")	


		#momo form
        momo_action		=	krcko.momo_action(info_text, [continue_action, eat_action, drop_action],\
                                [continue_option_text, eat_option_text, drop_option_text],\
                                    [continue_key, eat_key, drop_key])
		#insert
        self.turn_machine.insert_action(momo_action)          
        


    



sys_instance = Food()