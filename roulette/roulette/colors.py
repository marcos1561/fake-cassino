from enum import Enum, auto

def inverse_map(map: dict):
    inv_map = dict(zip(map.values(), map.keys()))
    return inv_map

class Color(Enum):
    black = 0
    red = 1
    white = 2

english_map = {
    Color.black: "black",
    Color.red: "red",
    Color.white: "white",
}

portuguese_map = {
    Color.black: "preto",
    Color.red: "vermelho",
    Color.white: "branco",
}

id_map = {
    Color.black: 0,
    Color.red: 1,
    Color.white: 2,
}


inv_english_map = inverse_map(english_map)
inv_portuguese_map = inverse_map(portuguese_map)
inv_id_map = inverse_map(id_map)

id_to_str = {c_id: english_map[inv_id_map[c_id]] for c_id in id_map.values()}

lan_to_map = {"en": english_map, "pt": portuguese_map}
lan_to_inv_map = {"en": inv_english_map, "pt": inv_portuguese_map}

class ColorMapper:
    colors = (Color.black, Color.red, Color.white)
    colors_ids = list(id_map.values())
    
    @classmethod
    def to_str(cls, color: Color, inverse=False, lang="en"):
        '''
        Parameters:
            lang: 
                Some value in ["en", "pt"].
        '''
        if not inverse:
            return lan_to_map[lang][color]
        else:
            return lan_to_inv_map[lang][color]
    
    @classmethod
    def to_id(cls, color: Color, inverse=False):
        if not inverse:
            return id_map[color]
        else:
            return inv_id_map[color]
    
    @classmethod
    def id_to_str(cls, id):
        return id_to_str[id]
        
if __name__ == "__main__":
    print(ColorMapper.id_to_str(0))
    print(ColorMapper.id_to_str(1))
    print(ColorMapper.id_to_str(2))