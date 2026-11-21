#include <iostream>
#include <string>

using conststr = char[10];

// Тривиально копируемая структура
struct StrCommands {
  conststr Left;
  conststr Right;
  conststr Put;
  conststr LargeRight;
  conststr LargeLeft;
};

class Idk {
private:
  char idx = 0; // char и символ, и 8-битное число Аля C
public:
  std::string res = "";

  Idk(const char* a) : res(a) {}

  void right() {
    idx++;
  }
  void left() {
    idx--;
  }

  void largeRight() {
    idx += 32;
  }
  void largeLeft() {
    idx -= 32;
  }
  
  void put() {
    res += idx;
  }

  std::string toCommands(const StrCommands& commands) {
    std::string r = "";
    char actualidx = 0; // Путь может быть отрицателен
    for (size_t a = 0; a<res.size(); a++) {
      char symb = res[a];
      int path = symb-actualidx;
      
      // Сколько надо сделать больших движков
      char larges = path / 32;

      bool mvToLeft = path < 0;
      bool hasMoves = path != 0;
      if (mvToLeft) {
          path*=-1;
          larges*=-1;
      }
      
      path -= larges*32;
      while (larges > 0) {
        larges--;
        r+= mvToLeft ? commands.LargeLeft : commands.LargeRight;
        if (larges > 0 | path > 0) r += " ";
      }
      while (path > 0) {
        path--;
        r+= mvToLeft ? commands.Left : commands.Right;
        if (path>0) r += " ";
      }
      actualidx = symb;
      if (hasMoves) r += " ";
      r+=commands.Put;
      if (a != res.size()-1) r += " ";
    }
    return r;
  }

  
  void executeCommands(const std::string& cmds, const StrCommands& commands) {
    const char* first = cmds.c_str();
    const char* end = first;
    const char* endIn = first+cmds.size();
    while (first != endIn) {
      end++;
      if (std::string_view(end,1)==" " || end == endIn) {
        // Интервал
        bool isEnd = end == endIn;
        std::string_view cmd(first,end);
        
        if (cmd == commands.Left) {
            left();
        } else if (cmd == commands.Right) {
            right();
        } else if (cmd == commands.Put) {
            put();
        } else if (cmd == commands.LargeLeft) {
            largeLeft();
        } else if (cmd == commands.LargeRight) {
            largeRight();
        } else {
            std::cout << "WARN: Unknown command " << cmd << std::endl;
        }
        
        if (!isEnd) first = end+1;
        else first = endIn;
      }
    }
  }
};

int main() {
  StrCommands cmds{
    "maow", "mew",
    "mrrrrr",
    "MAOW", "MEOW"
  };
  Idk writer{"I'm not cute anymore"};
  Idk anoth{""};
  
  auto c = writer.toCommands(cmds);
  anoth.executeCommands(c, cmds);
  
  std::cout << c << "\n\n\n" << std::endl;
  std::cout << anoth.res << std::endl;
  
  return 0;
}
