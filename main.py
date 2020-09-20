from certificates import gen_ca, gen_cert
from cmd import Cmd
from model import session, CA, CERT
from texttable import Texttable

'''
TOOD
    - export
    - logging
    - testing
'''


class MyPrompt(Cmd):
    def _get_san_input_int(self, message, bound):
        while True:
            try:
                val = input(message)
                int_val = int(val)
                if int_val < 1 or int_val > bound:
                    raise Exception()
                return int_val
            except Exception:
                print("Please verify.")
            else:
                break

    def _print_cas(self):
        '''Print existing CAs'''
        t = Texttable()
        ca_list = session.query(CA).all()
        for ca in ca_list:
            t.add_rows([['ID', 'Desc', 'CommonName'], str(ca).split(", ")])
        print(t.draw())
        return len(ca_list)

    def _print_certs(self):
        '''Print existing certs'''
        t = Texttable()
        cert_list = session.query(CERT).all()
        for cert in cert_list:
            t.add_rows(
                [['ID', 'Desc', 'CommonName', 'CA-ID'], str(cert).split(", ")]
            )
        print(t.draw())
        return len(cert_list)

    def do_exit(self, inp):
        '''Exit'''
        print("Bye")
        return True

    def do_addca(self, inp):
        '''Create a new CA'''
        cert, key = gen_ca()
        desc = input("Please enter an description: ")
        ca = CA(desc, cert, key)
        session.add(ca)
        session.commit()

    def do_addcert(self, inp):
        '''Add an CERT to an CA'''
        # Print existing CAs
        self._print_cas()

        # Get ca_id to export by user
        ca_id = input("CA to use for signing: ")

        # Extract from the DB
        ca = session.query(CA).filter(CA.id == ca_id).one()

        # Generate CERT, create an DB-Obj and add to session
        cert, key = gen_cert(ca)
        desc = input("Please enter an description: ")
        cert = CERT(desc, cert, key, ca)
        session.add(cert)
        session.commit()

    def do_getcas(self, inp):
        '''Get all CAs'''
        self._print_cas()

    def do_getcerts(self, inp):
        '''Get certs'''
        t = Texttable()
        for cert in session.query(CERT).all():
            t.add_rows(
                [['ID', 'Desc', 'CommonName', 'CA-ID'], str(cert).split(", ")]
            )
        print(t.draw())

    def do_getcertsforca(self, inp):
        '''Get all certs for an ca'''
        # Print existing CAs
        self._print_cas()

        # Let the user select the CA
        ca_id = input("Choose an CA by ID: ")

        # Print all CERTs for CA
        t = Texttable()
        for cert in session.query(CERT).filter(CERT.ca_id == ca_id).all():
            t.add_rows(
                [['ID', 'Desc', 'CommonName', 'CA-ID'], str(cert).split(", ")]
            )
        print(t.draw())

    def _get_cert_info_as_string(self, ca, what_to_export):
        '''Export whatever is selected'''
        if what_to_export == 1:
            return ca.get_key()
        elif what_to_export == 2:
            return ca.get_cert()
        elif what_to_export == 3:
            return ca.get_pub()
        else:
            raise Exception("Value out of range.")

    def _export_val(self, val):
        # Ask user for target
        t = Texttable()
        t.add_rows(
            [
                ['ID', 'Target'],
                ['1', 'File'],
                ['2', 'Console']
            ]
        )
        print(t.draw())

        target = self._get_san_input_int("Choose target: ", 2)

        if target == 1:
            # Export to file
            print("File")
            filename = input("Choose filename: ")
            f = open(filename, 'wb')
            f.write(val.encode('utf-8'))
            f.close()
            print("Data was saved to {}".format(filename))
        elif target == 2:
            # Export to console
            print(val)
        else:
            raise Exception("Waaaait, what?")

    def do_exportca(self, inp):
        '''Export an key or cert of the ca'''
        num_cas = self._print_cas()
        ca_id = self._get_san_input_int("Choose an CA to export: ", num_cas)
        ca = session.query(CA).filter(CA.id == ca_id).one()

        # Ask user what to export
        t = Texttable()
        t.add_rows(
            [
                ['ID', 'Target'],
                ['1', 'private key'],
                ['2', 'certificate'],
                ['3', 'public key']
            ]
        )
        print(t.draw())
        what_to_export = self._get_san_input_int("What to export :", 3)
        val = self._get_cert_info_as_string(ca, what_to_export)

        self._export_val(val)

    def do_exportcert(self, inp):
        '''Export an key or cert of an client-cert'''
        num_certs = self._print_certs()
        cert_id = self._get_san_input_int(
            "Choose an certificate to export: ",
            num_certs
        )
        print(cert_id, type(cert_id))
        cert = session.query(CERT).filter(CERT.id == cert_id).one()

        # Ask user what to export
        t = Texttable()
        t.add_rows(
            [
                ['ID', 'Target'],
                ['1', 'private key'],
                ['2', 'certificate'],
                ['3', 'public key']
            ]
        )
        print(t.draw())

        what_to_export = self._get_san_input_int("What to export :", 3)
        val = self._get_cert_info_as_string(cert, what_to_export)

        self._export_val(val)


MyPrompt().cmdloop()
