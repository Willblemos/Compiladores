
#include <iostream>
#include <fstream>
using namespace std;



string V(string txt){
    char a = txt[0];
    if(a >= 'a' && a<= 'z'){
    	cout << "V aceitou:" << a << endl; 
        return txt.substr(1);
    }
    else 
        return false;
        }


char number(char c){
    char b = '*';
    int a = c -48;
    
    
    if(a >= 0 && a <= 9){
        return c;
    }
    else
        return b; 
}

string L(string txt){
    string result;
    if(number(txt[0]) != '*'){
    	cout << "prox L:" <<  txt[0] << endl; 
        result = L(txt.substr(1));    
       return txt;
    }
    else if(txt[0] >= 'A' && txt[0] <= 'Z'){
    	cout << "prox L:" <<   txt[0] << endl; 
        result = L(txt.substr(1));
       return txt;
    }
    else if( txt[0] == '$'){
        cout << "aceitou L: " <<  txt[0] << endl; 
        return txt;
    }
    else 
        return false;
    
}


string E(string txt){
    string result;
    char b = '*';
    
    if((txt[0] >= 'a' && txt[0] <= 'z')){
        cout << "aceitou E :" << txt[0] << endl;
        return txt;
    }
    
    else if(number(txt[0]) != '*'){
    	cout << "prox E : " <<  txt[0] << endl; 
        result = L(txt.substr(1));   
		
    }
    
    else if(txt[0] >= 'A' && txt[0] <= 'Z'){
    	cout << "prox E :" <<  txt[0] << endl; 
        result = L(txt.substr(1));
        cout << "saiu do L" << result << endl;
        return result;
    }
    
     else if(txt[0] == '$'){
        cout << "prox E : " <<  txt[0] << endl;
		result = V(txt.substr(1));
		cout << result << endl;
        if ((result[0]) && result[0] == '.'){
        	result = E(txt.substr(3));
		} else 
			cout << "erro" << endl;
			
        
    }
    
    
    else if (txt[0] == '('){
    	cout << "prox (E : " <<  txt[0] << endl;
		result = E(txt.substr(1));
		//cout << "testeA" << result << endl;
		if((result[0])){
		//	cout << "teste" << result << endl;
			
			result = E(result.substr(1));
			cout << "prox 2 E:" <<  result[0] << endl;
			
			if((result[0])){
				result = result.substr(1);
				
				if(result[0] == ')'){
				cout << "aceitou: " << result << endl;
				}
				
			
				 
			}
			
			
		} 
		
		
	}
      
}



int main()
{
	
  string s;
string sTotal;

ifstream in;
in.open("example.txt");

while(!in.eof()) {
	getline(in, s);
	sTotal += s + "\n";
	
}

cout << "texto: " << sTotal<<endl;

in.close();	


E(s);
    
}




